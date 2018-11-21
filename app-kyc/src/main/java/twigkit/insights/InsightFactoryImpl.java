package twigkit.insights;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.insights.model.Insight;
import twigkit.model.Query;
import twigkit.model.Response;
import twigkit.model.Result;
import twigkit.platform.Platform;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.*;
import java.util.stream.Collectors;

public class InsightFactoryImpl implements InsightFactory {

    private static final Logger logger = LoggerFactory.getLogger(InsightFactoryImpl.class);

    private Insight insight;

    private static int MAX_TIME = 2500;
    private static int BATCH_SIZE = 100;

    public InsightFactoryImpl(Platform platform, Query query) {
        insight = new Insight();

        query.setResultsPerPage(BATCH_SIZE);
        query.setMaxResults(BATCH_SIZE);

        Response canonical = platform.search(query);

        long hits = canonical.getHits().getActual();
        long time = canonical.getQueryTime() > 0 ? canonical.getQueryTime() : 1;

        int maxFetches = MAX_TIME / (int) time;
        maxFetches = Math.min(10, maxFetches);

        long offset = (hits - (Math.max(maxFetches, 2) * BATCH_SIZE)) / Math.max(maxFetches, 2);

        if (offset < BATCH_SIZE) {
            offset = BATCH_SIZE;
        }

        logger.debug("Sampling from {} hits retrieved in {} ms.", hits, time);
        logger.debug("Estimated offset is {}", offset);
        sample(platform, query, canonical, hits, maxFetches, offset);

        response(canonical);
    }

    private void sample(Platform platform, Query query, Response canonical, long hits, int maxFetches, long offset) {
        int requests = 1;

        logger.debug("Estimating to do {} requests in batches of {}", maxFetches, BATCH_SIZE);

        while (canonical.getQueryTime() < MAX_TIME
                && requests <= maxFetches
                && query.getOffset() + BATCH_SIZE < hits) {

            query.setPage(query.getPage() + (offset / query.getResultsPerPage()));

            logger.debug("Fetching with offset of {}, elapsed time is {} ms.", query.getOffset(), canonical.getQueryTime());

            Response supplement = platform.search(query);
            combine(canonical, supplement);
            requests++;
        }
        logger.debug("Completed {} requests in {} ms.", requests, canonical.getQueryTime());
    }

    private void combine(Response canonical, Response supplement) {
        canonical.setQueryTime(canonical.getQueryTime() + supplement.getQueryTime());
        canonical.getResults().addAll(supplement.getResults());
    }

    public Insight insight() {
        return insight;
    }

    private void response(Response response) {
        insight.sample_count(response.getResults().size());
        insight.hits(response.getHits().getActual());

        response.getFacets().values().forEach(insight::facet);
        response.getResults().forEach(this::result);

        insight.fields().entrySet().stream()
                .filter(e -> e.getValue().cardinality() <= 0.25)
                .filter(e -> !(e.getValue().distinct() == 1))
                .filter(e -> !(e.getValue().average_length() == 100))
                .filter(e -> !(e.getValue().occurrences() == e.getValue().distinct()))
                .filter(e -> !insight.facets().containsKey(e.getKey()))
                .forEach(e -> insight.facet_suggestions().add(e.getKey()));

        insight.fields().entrySet().stream()
                .filter(e -> e.getValue().cardinality() == 1)
                .filter(e -> e.getValue().occurrences() == insight.sample_count())
                .forEach(e -> insight.unique_fields().add(e.getKey()));

        // Suggest titles
        insight.fields().values().stream()
                .filter(f -> f.cardinality() > 0.80)
                .filter(f -> f.coverage() > 0.75)
                .filter(f -> f.types().size() == 1)
                .filter(f -> f.types().contains(String.class.getTypeName()))
                .forEach((Insight.Field f) -> {
                    int urlCount = 0;
                    int titleCharCount = 0;
                    for (String value : f.all_values()) {
                        try {
                            // Checking for characters that indicate a title
                            if (value.contains(" ")) {
                                titleCharCount++;
                            }
                            // Check if value is a URL
                            new URL(value);
                            urlCount++;
                        } catch (MalformedURLException e) {
                        }
                    }
                    if ((double) (urlCount / f.all_values().size()) > 0.5) {
                        insight.url_fields().add(f.name());
                        insight.title_suggestions().remove(f.name());
                    }

                    if (((double) titleCharCount / f.all_values().size()) > 0.5) {
                        if (!insight.title_suggestions().contains(f.name().replaceAll("_[A-z]{1,3}$", ""))) {
                            insight.title_suggestions().add(f.name());
                        }
                    }
                });

        // Suggest descriptions
        insight.fields().values().stream()
                .filter(f -> f.cardinality() > 0.5)
                .filter(f -> f.types().size() == 1)
                .filter(f -> f.coverage() > 0.60)
                .filter(f -> f.types().contains(String.class.getTypeName()))
                .forEach(f -> {
                    if (f.average_length() > 200) {
                        if (!insight.description_suggestions().contains(f.name().replaceAll("_[A-z]{1,3}$", ""))) {
                            insight.description_suggestions().add(f.name());
                        }
                    }

                    if (f.name().toLowerCase().equals("body") ||
                            f.name().toLowerCase().contains("description") ||
                            f.name().toLowerCase().equals("text") ||
                            f.name().toLowerCase().equals("summary")) {
                        insight.description_suggestions().add(f.name());
                    }
                });


        insight.fields().values().stream().forEach(f -> {
            // Gather random samples
            f.sample();

            // Normalising correlations
            Set<String> remove = new HashSet<>();
            f.correlated_fields().keySet().stream()
                    .forEach(name -> {
                        float normalised = (f.correlated_fields().get(name).floatValue() / insight.sample_count());
                        // Filtering out less common edges
                        if (normalised > 0.75f) {
                            f.correlated_fields().put(name, normalised);
                        } else {
                            remove.add(name);
                        }
                    });
            remove.stream().forEach(name -> f.correlated_fields().remove(name));

            f.correlated_fields(sortByValue(f.correlated_fields()));
        });
    }

    private void result(Result result) {
        result.getFields().values().stream()
                .filter(f -> !insight.facets().containsKey(f.getName()))
                .filter(f -> !f.getName().startsWith("_lw_"))
                .filter(f -> !f.getName().startsWith("ows_"))
                .filter(f -> !f.getName().startsWith("xmpMM"))
                .filter(f -> !f.getName().startsWith("xmpTP"))
                .filter(f -> !f.getName().startsWith("xmp_"))
                .filter(f -> !f.getName().startsWith("access_permission"))
                .sorted((f1, f2) -> f1.getName().compareTo(f2.getName()))
                .forEach(f -> {
                    Insight.Field field = insight.field(f);

                    result.getFields().keySet().stream()
                            .filter(name -> !name.startsWith("_lw_"))
                            .filter(name -> !name.startsWith("ows_"))
                            .filter(name -> !name.startsWith("xmpMM"))
                            .filter(name -> !name.startsWith("xmpTP"))
                            .filter(name -> !name.startsWith("xmp_"))
                            .filter(name -> !name.startsWith("access_permission"))
                            .forEach(name -> field.add_correlated_field(name));
                });
    }

    private static <K, V extends Comparable<? super V>> Map<K, V> sortByValue(Map<K, V> map) {
        return map.entrySet()
                .stream()
                .sorted(Map.Entry.comparingByValue(Collections.reverseOrder()))
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        Map.Entry::getValue,
                        (e1, e2) -> e1,
                        LinkedHashMap::new
                ));
    }
}
