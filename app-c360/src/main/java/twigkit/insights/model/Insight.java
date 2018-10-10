package twigkit.insights.model;

import org.apache.commons.collections.map.HashedMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.insights.InsightFactoryImpl;
import twigkit.model.DataObject;
import twigkit.model.Key;
import twigkit.ui.jsp.util.FieldSummariser;
import twigkit.util.StringUtils;

import java.text.Collator;
import java.util.*;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.ThreadLocalRandom;

public class Insight extends DataObject {

    private static final Logger logger = LoggerFactory.getLogger(Insight.class);

    @Key
    private int sample_count;

    @Key
    private long hits;

    @Key
    private Set<String> unique_fields;

    @Key
    private Set<String> url_fields;

    @Key
    private Set<String> title_suggestions;

    @Key
    private Set<String> description_suggestions;

    @Key
    private Set<String> facet_suggestions;

    @Key
    private Map<String, Field> fields;

    @Key
    private Map<String, Field> facets;

    public Insight() {
        final Collator usCollator = Collator.getInstance(Locale.US);
        usCollator.setStrength(Collator.PRIMARY);

        fields = new ConcurrentSkipListMap<>(usCollator);
        unique_fields = new HashSet<>();
        url_fields = new HashSet<>();
        facets = new LinkedHashMap<>();
        title_suggestions = new HashSet<>();
        title_suggestions = new HashSet<>();
        description_suggestions = new HashSet<>();
        facet_suggestions = new HashSet<>();
    }

    public Insight.Field field(twigkit.model.Field field) {
        if (!fields.containsKey(field.getName())) {
            fields.put(field.getName(), new Field(this, field.getName()));
        }

        Insight.Field fi = fields.get(field.getName());
        for (Object obj : field.getValues()) {
            fi.value(field.getValue().getActual());
        }

        return fi;
    }

    public Insight.Field facet(twigkit.model.Facet facet) {
        Insight.Field fi = new Field(this, facet.getField());
        fi.distinct(facet.getFilters().size());
        fi.occurrences((int) facet.getSumOfCounts());
        fi.cardinality((float) fi.occurrences() / hits());

        facet.getFilters().stream().map(facetFilter -> facetFilter.getValue().getActualAsString()).mapToInt(String::length).average().ifPresent(fi::average_length);
        facet.getFilters().forEach(facetFilter -> fi.types(facetFilter.getValue().getActual().getClass().getTypeName()));
        facet.getFilters().stream().filter(facetFilter -> facetFilter.getValue().getActualAsString().length() > 0).limit(5).forEach(facetFilter -> fi.sample().add(facetFilter.getValue().getActual()));

        facets.put(facet.getField(), fi);

        return fi;
    }

    public Set<String> unique_fields() {
        return unique_fields;
    }

    public Set<String> url_fields() {
        return url_fields;
    }

    public Set<String> facet_suggestions() {
        return facet_suggestions;
    }

    public Set<String> title_suggestions() {
        return title_suggestions;
    }

    public Set<String> description_suggestions() {
        return description_suggestions;
    }

    public Map<String, Field> fields() {
        return fields;
    }

    public Map<String, Field> facets() {
        return facets;
    }

    public int sample_count() {
        return sample_count;
    }

    public Insight sample_count(int count) {
        this.sample_count = count;
        return this;
    }

    public long hits() {
        return hits;
    }

    public Insight hits(long hits) {
        this.hits = hits;
        return this;
    }

    public class Field extends DataObject {

        private Insight insight;
        private Set<String> all_values;

        @Key
        private String name;

        @Key
        private Set<String> types;

        @Key
        private Set<Object> sample;

        @Key
        private int occurrences;

        @Key
        private Map<String, Float> correlated_fields;

        @Key
        private float coverage;

        @Key
        private int distinct;

        @Key
        private float cardinality;

        @Key
        private int average_length;

        Field(Insight insight, String name) {
            this.insight = insight;
            this.name = name;
            all_values = new HashSet<>();
            sample = new HashSet<>();
            types = new HashSet<>();
            correlated_fields = new HashedMap();
        }

        public String name() {
            return name;
        }

        public Set<String> types() {
            return types;
        }

        public Set<Object> sample() {
            if (all_values().size() > 0) {
                sample = new HashSet<>();
                List<Object> samples = new ArrayList<>(all_values());

                logger.trace("Sampling field: {} ({})", name(), samples.size());
                if (samples.size() < 6) {
                    sample.addAll(samples);
                } else {
                    Set<Integer> used = new HashSet<>();
                    int bucket = samples.size() / 5;
                    int offset = 0;
                    for (int i = 0; i < 6; i++) {
                        int pos = 0;
                        int passes = 0;
                        while (used.contains(pos) && passes < samples.size() && offset < samples.size()) {
                            pos = ThreadLocalRandom.current().nextInt(Math.min(bucket, samples.size() - offset));
                            pos = offset + pos;
                            passes++;
                        }
                        used.add(pos);
                        logger.trace("> {} ({} - {})", pos, offset, Math.min(offset + bucket, samples.size()));
                        offset = Math.min(offset + bucket, samples.size());
                        String value = samples.get(pos).toString();
                        value = FieldSummariser.limitLength(value, 250);
                        sample.add(value);
                    }
                }
            }
            return sample;
        }

        public Field types(String types) {
            this.types.add(types);
            return this;
        }

        public int occurrences() {
            return occurrences;
        }

        public Field occurrences(int occurrences) {
            this.occurrences = occurrences;
            return this;
        }

        public Map<String, Float> correlated_fields() {
            return correlated_fields;
        }

        public Field add_correlated_field(String field_name) {
            if (!correlated_fields.containsKey(field_name)) {
                correlated_fields.put(field_name, 0f);
            }
            correlated_fields.put(field_name, correlated_fields.get(field_name).intValue() + 1f);

            return this;
        }

        public Field correlated_fields(Map<String, Float> correlated_fields) {
            this.correlated_fields = correlated_fields;
            return this;
        }

        public float coverage() {
            return coverage;
        }

        public Field coverage(float coverage) {
            this.coverage = coverage;
            return this;
        }

        public int distinct() {
            return distinct;
        }

        public Field distinct(int distinct) {
            this.distinct = distinct;
            return this;
        }

        public float cardinality() {
            return cardinality;
        }

        public Field cardinality(float cardinality) {
            this.cardinality = cardinality;
            return this;
        }

        public int average_length() {
            return average_length;
        }

        public Field average_length(double average_length) {
            this.average_length = (int) average_length;
            return this;
        }

        public Set<String> all_values() {
            return all_values;
        }

        Field value(Object value) {
            if (value.toString().length() > 0) {
                all_values.add(value.toString());

                types.add(value.getClass().getTypeName());
                occurrences++;
                coverage = (float) occurrences() / (float) sample_count();
                distinct = all_values.size();
                cardinality = (float) distinct / occurrences();

                average_length = (int) all_values.stream().mapToInt(String::length).average().getAsDouble();
            }
            return this;
        }
    }
}
