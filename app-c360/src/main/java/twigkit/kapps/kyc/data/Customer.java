package twigkit.kapps.kyc.data;

import java.util.ArrayList;
import java.util.List;

public class Customer {

    private int age;
    private boolean married;
    private int value;

    private List<Product> products;
    private List<Product> recommendations;

    public Customer(int age, boolean married, int value) {
        this.age = age;
        this.married = married;
        this.value = value;
        this.products = new ArrayList<Product>();
        this.recommendations = new ArrayList<Product>();
    }

    public void addProduct(Product product) {
        this.products.add(product);
    }

    public void addRecommendation(Product product) {
        this.recommendations.add(product);
    }

    public List<Product> getProducts() {
        return products;
    }

    public List<Product> getRecommendations() {
        return recommendations;
    }

    public int getAge() {
        return age;
    }

    public boolean isMarried() {
        return married;
    }

    public int getValue() {
        return value;
    }

    @Override
    public String toString() {
        return "Customer{" +
                "value=" + value +
                ", married=" + married +
                ", age=" + age +
                '}';
    }
}
