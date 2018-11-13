package twigkit.client.processor.response;

import twigkit.model.Value;
import twigkit.search.processors.AbstractNamedFieldValueProcessor;

import java.text.NumberFormat;

/**
 *
 * @author JohnGUnderwood
 */
public class PercentFormatProcessor extends AbstractNamedFieldValueProcessor {

    private NumberFormat nfp = NumberFormat.getPercentInstance();
    private NumberFormat nfi = NumberFormat.getIntegerInstance();


    @Override
    public Value processValue(Value value) {
        Double fval = (Double) value.getActual();
        value.setActual(nfi.format(fval * 100));
        value.setDisplay(nfp.format(fval));
        return value;
    }
}


