import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import com.cburch.logisim.file.*;
import com.cburch.logisim.circuit.*;
import com.cburch.logisim.comp.Component;
import com.cburch.logisim.instance.*;
import com.cburch.logisim.std.wiring.Pin;
import com.cburch.logisim.data.*;
import com.cburch.logisim.proj.Project;

/** Estudio aislado: usa los generadores y el evaluador reales, sin editar el .circ.
 * El saldo es matematico: no aplica bloqueo en cero ni desbordamiento de 8 bits.
 */
public class EstudioResultados {
    static Component pin(CircuitState state, String label) {
        for (Component c : state.getCircuit().getNonWires()) {
            if (c.getFactory() instanceof Pin && label.equals(c.getAttributeSet().getValue(StdAttr.LABEL))) return c;
        }
        throw new IllegalArgumentException("Pin no encontrado: " + label);
    }
    static void set(CircuitState state, String label, int value) {
        Component c = pin(state, label);
        InstanceState instance = state.getInstanceState(c);
        Pin.FACTORY.setValue(instance, Value.createKnown(Pin.FACTORY.getWidth(instance.getInstance()), value));
        state.markComponentAsDirty(c);
        state.getPropagator().propagate();
    }
    static int get(CircuitState state, String label) {
        return Pin.FACTORY.getValue(state.getInstanceState(pin(state, label))).toIntValue();
    }
    public static void main(String[] args) throws Exception {
        if (args.length != 3) throw new IllegalArgumentException("Uso: EstudioResultados archivo.circ cantidad salida.csv");
        int count = Integer.parseInt(args[1]);
        if (count <= 0) throw new IllegalArgumentException("La cantidad debe ser positiva");
        LogisimFile file = new Loader(null).openLogisimFile(new File(args[0]));
        Project project = new Project(file);
        CircuitState generator = new CircuitState(project, file.getCircuit("generador_resultados"));
        CircuitState evaluator = new CircuitState(project, file.getCircuit("evaluador_premios"));
        generator.getPropagator().propagate();
        evaluator.getPropagator().propagate();
        set(generator, "Generar", 0);
        Path output = Paths.get(args[2]);
        if (output.toAbsolutePath().getParent() != null) Files.createDirectories(output.toAbsolutePath().getParent());
        int balance = 10, victories = 0, firstZero = 0;
        try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            writer.write("tirada,resultado_1,resultado_2,resultado_3,premio,hay_premio,saldo_teorico\n");
            for (int draw = 1; draw <= count; draw++) {
                set(generator, "Generar", 1);
                int a = get(generator, "Resultado 1"), b = get(generator, "Resultado 2"), c = get(generator, "Resultado 3");
                if (a < 0 || a > 2 || b < 0 || b > 2 || c < 0 || c > 2) throw new AssertionError("Simbolo invalido en " + draw);
                set(evaluator, "Resultado 1", a); set(evaluator, "Resultado 2", b); set(evaluator, "Resultado 3", c);
                int prize = get(evaluator, "Premio"), win = get(evaluator, "HayPremio");
                int expected = a == b && b == c ? 3 - a : 0;
                if (prize != expected || win != (expected > 0 ? 1 : 0)) throw new AssertionError("Premio incorrecto en " + draw);
                balance += prize - 1;
                if (win == 1) victories++;
                if (firstZero == 0 && balance <= 0) firstZero = draw;
                writer.write(draw + "," + a + "," + b + "," + c + "," + prize + "," + win + "," + balance + "\n");
                set(generator, "Generar", 0);
                if (get(generator, "Resultado 1") != a || get(generator, "Resultado 2") != b || get(generator, "Resultado 3") != c) throw new AssertionError("Resultado cambia al soltar Generar");
            }
        }
        System.out.println("Tiradas=" + count + "; victorias=" + victories + "; saldo teorico=" + balance + "; primera llegada a cero=" + firstZero);
        System.exit(0);
    }
}
