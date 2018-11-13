package twigkit.kapps.kyc.data;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import org.joda.time.DateTime;
import org.joda.time.Years;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.search.gsa.GSAPlatform;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.Set;

public class ProcessCustomersDataFile {

    private static final Logger logger = LoggerFactory.getLogger(ProcessCustomersDataFile.class);

    private List<Product> allProducts;

    private Random rand = new Random(System.currentTimeMillis()); // would make this static to the class

    public ProcessCustomersDataFile() {
        this.allProducts = new ArrayList<Product>();
        this.allProducts.add(new Product("junior_ira", "IRA for Minors", Integer.MIN_VALUE, false, Integer.MIN_VALUE, 18));
        this.allProducts.add(new Product("traditional_ira", "Traditional IRA", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("roth_ira", "Roth IRA", Integer.MIN_VALUE, false, 18, 60));
        this.allProducts.add(new Product("hsa", "Health Savings Account (HSA)", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("home_insurance", "Home Insurance", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("travel_insurance", "Travel Insurance", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("car_insurance", "Car Insurance", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("family_insurance", "Family Insurance", Integer.MIN_VALUE, true, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("current_account", "Current Account", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("savings_account", "Savings Account", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("premier_account", "Premier Account", 2000, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("credit_card", "Credit Card", Integer.MIN_VALUE, false, 18, Integer.MAX_VALUE));
        this.allProducts.add(new Product("premier_credit_card", "Premier Credit Card", 2000, false, 18, Integer.MAX_VALUE));
    }

    private static SimpleDateFormat sourceFormat = new SimpleDateFormat("MM/dd/yyyy mm:ss:SS");
    private static SimpleDateFormat targetFormat = GSAPlatform.dateFormat();

    public void process(String path, File outputFolder) throws Throwable {
        File csvData = new File(path);
        CSVParser parser = CSVParser.parse(csvData, Charset.defaultCharset(), CSVFormat.DEFAULT.withHeader());
        CSVPrinter printer = new CSVPrinter(new FileWriter(new File(outputFolder, "customer.csv")), CSVFormat.DEFAULT);

        // Print header.
        Set<String> headers = parser.getHeaderMap().keySet();
        for (String columnHeader: headers) {
            printer.print(columnHeader);
        }
        for (int i = 0; i < allProducts.size(); i++) {
            printer.print("current_products_" + i);
        }
        for (int i = 0; i < allProducts.size(); i++) {
            printer.print("recommended_products_" + i);
        }
        printer.println();

        for (CSVRecord record: parser) {

            DateTime dob = new DateTime(sourceFormat.parse(record.get("dob")));
            DateTime now = new DateTime();
            int age = Years.yearsBetween(dob, now).getYears();
            boolean married = record.get("marital_status") != null && record.get("marital_status").equalsIgnoreCase("Married");
            int lifetimeValue = Integer.parseInt(record.get("lifetime_value"));

            for (String column: headers) {
                String value = record.get(column);
                if (column.equalsIgnoreCase("dob") || column.equalsIgnoreCase("customer_since")) {
                    value = targetFormat.format(sourceFormat.parse(value));
                }
                printer.print(value);
            }

            Customer customer = new Customer(age, married, lifetimeValue);
            assignProducts(customer);

            printProducts(customer.getProducts(), printer);
            printProducts(customer.getRecommendations(), printer);

            printer.println();
        }
        printer.close();
        parser.close();
    }

    private void printProducts(List<Product> products, CSVPrinter printer) throws IOException {
        int i = 0;
        while (i < products.size()) {
            printer.print(products.get(i).getName());
            i++;
        }

        // Need to pad up to the allProducts.size() mark, to ensure the CSV headers match up.
        for (int j = i; j < allProducts.size(); j++) {
            printer.print("");
        }
    }

    public void assignProducts(Customer customer) {

        List<Product> products = new ArrayList<Product>(this.allProducts);
        int n = rand.nextInt(allProducts.size() >> 1);
        for (int i = 0; i < n; i++) {
            Product product = products.remove(rand.nextInt(products.size()));
            if (product.isEligible(customer)) {
                customer.addProduct(product);
                logger.trace("Adding product {}", product.getId());
            } else {
                logger.trace("{} is not eligible for {}", customer, product.getId());
            }
        }

        // Run through remaining products and add to the list of recommendations for the customer.
        for (Product product: products) {
            if (product.isEligible(customer)) {
                customer.addRecommendation(product);
                logger.trace("Adding recommended product {}", product.getId());
            } else {
                logger.trace("{} is not eligible for {}", customer, product.getId());
            }
        }
    }


    public static String translateDate(String nativeDate) throws Throwable {
        return targetFormat.format(sourceFormat.parse(nativeDate));
    }

    public static void main(String[] args) throws Throwable {
        ProcessCustomersDataFile processor = new ProcessCustomersDataFile();
        processor.process(args[0], new File(args[1]));
    }
}