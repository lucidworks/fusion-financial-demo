package twigkit.client.processor.response;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twigkit.model.Value;
import twigkit.search.processors.AbstractNamedFieldValueProcessor;

import java.text.NumberFormat;

/**
 *
 * @author JohnGUnderwood
 */
public class NumberFormatProcessor extends AbstractNamedFieldValueProcessor {

    private static final Logger logger = LoggerFactory.getLogger(NumberFormatProcessor.class);

    private NumberFormat nf = NumberFormat.getNumberInstance();

    @Override
    public Value processValue(Value value) {
        nf.setMaximumFractionDigits(2);
        Float fval = (Float) value.getActual();
        if(fval < 1000000000){
            value.setDisplay("$"+nf.format(fval / 1000000) + "M");
//            value.setActual("$"+nf.format(fval / 1000000) + "M");

        }else {
            value.setDisplay("$"+nf.format(fval / 1000000000) + "B");
//            value.setActual("$"+nf.format(fval / 1000000000) + "B");
        }

        return value;
    }
}


