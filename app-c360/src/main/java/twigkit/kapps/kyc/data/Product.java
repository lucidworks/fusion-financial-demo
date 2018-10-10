package twigkit.kapps.kyc.data;

public class Product {

    private String id;
    private String name;
    private int minimumValue;
    private boolean forFamilies;
    private int minimumAge;
    private int maximumAge;

    public Product(String id, String name, int minimumValue, boolean forFamilies, int minimumAge, int maximumAge) {
        this.id = id;
        this.name = name;
        this.minimumValue = minimumValue;
        this.forFamilies = forFamilies;
        this.minimumAge = minimumAge;
        this.maximumAge = maximumAge;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public int getMinimumValue() {
        return minimumValue;
    }

    public void setMinimumValue(int minimumValue) {
        this.minimumValue = minimumValue;
    }

    public boolean isForFamilies() {
        return forFamilies;
    }

    public void setForFamilies(boolean forFamilies) {
        this.forFamilies = forFamilies;
    }

    public int getMinimumAge() {
        return minimumAge;
    }

    public void setMinimumAge(int minimumAge) {
        this.minimumAge = minimumAge;
    }

    public int getMaximumAge() {
        return maximumAge;
    }

    public void setMaximumAge(int maximumAge) {
        this.maximumAge = maximumAge;
    }

    public boolean isEligible(Customer customer) {
        return
            (customer.getValue() >= getMinimumValue()) &&
            (customer.getAge() >= getMinimumAge()) &&
            (customer.getAge() <= getMaximumAge()) &&
            (!isForFamilies() || customer.isMarried())
                ;
    }
}
