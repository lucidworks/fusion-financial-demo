package twigkit.fusion;

import twigkit.model.DataObject;
import twigkit.model.Key;

import java.util.Objects;

/**
 *  DataObject for the JSON postbody sent to <code>FusionConfigurationResource</code> to get a Fusion session.
 */
class FusionSessionRequest extends DataObject {

    @Key
    private String user;

    @Key
    private String password;

    @Key
    private String realm;

    public String getUser() {

        return user;
    }

    public void setUser(String user) {
        this.user = user;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getRealm() {
        return realm;
    }

    public void setRealm(String realm) {
        this.realm = realm;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        if (!super.equals(o)) return false;
        FusionSessionRequest that = (FusionSessionRequest) o;
        return Objects.equals(user, that.user) &&
                Objects.equals(password, that.password) &&
                Objects.equals(realm, that.realm);
    }

    @Override
    public int hashCode() {
        return Objects.hash(super.hashCode(), user, password, realm);
    }
}
