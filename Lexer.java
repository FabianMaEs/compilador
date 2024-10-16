import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Lexer {
    private static final String[] RESERVED_WORDS = { "program", "if", "else", "do", "while", "read", "write",
            "float", "int", "bool", "not", "and", "or", "true", "false", "then" };
    
    private static final HashMap<String, String> RESERVED_WORDS_MAP = createReservedWordsMap();
    private static final HashMap<String, String> SYMBOLS_MAP = createSymbolsMap();

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Error: java Lexer <archivo> | Se esperaba un argumento con el nombre del archivo.");
            return;
        }

        String fileName = args[0];
        String code = readFile(fileName);
        
        if (code.isEmpty()) {
            System.err.println("El archivo está vacío o no se pudo leer.");
            return;
        }

        ArrayList<Token> tokens = lex(code);

        for (Token token : tokens) {
            System.out.println(token);
        }
    }

    public static ArrayList<Token> lex(String code) {
        ArrayList<Token> tokens = new ArrayList<>();
        Pattern pattern = Pattern.compile(getRegexPattern());
        Matcher matcher = pattern.matcher(code);
        int row = 1;
        int column = 1;

        while (matcher.find()) {
            String match = matcher.group();
            TokenType type = getTokenType(match);
            String key = getTypeKey(type, match);
        
            // Manejar saltos de línea
            if (match.contains("\n")) {
                row++;
                column = 1; // Reiniciar la columna en cada nueva línea
                // Continuar con el siguiente token
                continue;
            } 
        
            // Agregar el token con la columna actual (antes de que se incremente) si no es un comentario
            if (type != TokenType.COMENTARIO_CORTO && type != TokenType.COMENTARIO_LARGO)
                tokens.add(new Token(type, match, key, row, column));
        
            // Aumentar la columna según la longitud del match
            column += match.length();
        }        
        return tokens;
    } 

    private static TokenType getTokenType(String match) {
        if (match.startsWith("//")) {
            return TokenType.COMENTARIO_CORTO;
        } else if (match.startsWith("/*")) {
            return TokenType.COMENTARIO_LARGO;
        } else if (match.matches("\\d+(\\.\\d+)?")) {
            return TokenType.NÚMERO;
        } else if (match.matches("\"[^\"]*\"|'[^']*'")) {
            return TokenType.CADENA;
        } else if (match.matches(getReservedWordsRegex())) {
            return TokenType.PALABRA_RESERVADA;
        }
        else if (match.matches("!=|==|<=|>=|&&|\\|\\|")) {
            return TokenType.SÍMBOLO;
        } 
        else if (match.matches("[-+*/^<>!=;,(){}]")) {
            return TokenType.SÍMBOLO;
        }
         else if (match.matches("\\w+")) {
            return TokenType.IDENTIFICADOR;
        } else {
            return TokenType.DESCONOCIDO;
        }
    }
    
    
    private static String getTypeKey(TokenType type, String match) {
        switch (type) {
            case NÚMERO:
                return "NUM";
            case PALABRA_RESERVADA:
                return mapReservedWordToKey(match);
            case SÍMBOLO:
                return mapSymbolToKey(match);
            case IDENTIFICADOR:
                return "ID";
            case COMENTARIO_CORTO:
                return "COC";
            case COMENTARIO_LARGO:
                return "COL";
            default:
                return "";
        }
    }
    
    private static String getRegexPattern() {
        return "\"[^\"]*\"|'[^']*'|//.*|/\\*(.|\\R)*?\\*/|\\b(" + getReservedWordsRegex() + ")\\b|\\d+(\\.\\d+)?|!=|<=|>=|&&|\\|\\||==|\\w+|[-+*/^<>!;,(){}]|\\n|\\S";

    }    

    private static String getReservedWordsRegex() {
        return String.join("|", RESERVED_WORDS);
    }

    private static String mapReservedWordToKey(String word) {
        return RESERVED_WORDS_MAP.getOrDefault(word, "");
    }

    private static String mapSymbolToKey(String symbol) {
        return SYMBOLS_MAP.getOrDefault(symbol, "");
    }
    
    private static HashMap<String, String> createReservedWordsMap() {
        HashMap<String, String> map = new HashMap<>();
        map.put("program", "PRO");
        map.put("if", "IF");
        map.put("else", "ELS");
        map.put("do", "DO");
        map.put("while", "WHI");
        map.put("read", "REA");
        map.put("write", "WRI");
        map.put("float", "FLO");
        map.put("int", "INT");
        map.put("bool", "BOO");
        map.put("not", "NOT");
        map.put("and", "AND");
        map.put("or", "OR");
        map.put("true", "TRU");
        map.put("false", "FAL");
        map.put("then", "THN");
        return map;
    }

    private static HashMap<String, String> createSymbolsMap() {
        HashMap<String, String> map = new HashMap<>();
        map.put("+", "MAS");
        map.put("-", "MEN");
        map.put("*", "MUL");
        map.put("/", "DIV");
        map.put("^", "POT");
        map.put("<", "MOR");
        map.put(">", "MAR");
        map.put("=", "IGU");
        map.put("!", "NOT");
        map.put(";", "PYC");
        map.put(",", "COM");
        map.put("(", "PA");
        map.put(")", "PC");
        map.put("{", "LLA");
        map.put("}", "LLC");
        map.put("!=", "NEQ");
        map.put("<=", "LEQ");
        map.put(">=", "GEQ");
        map.put("&&", "AND");
        map.put("||", "OR");
        map.put("==", "EQL");
        map.put("AND", "AND");
        map.put("OR", "OR");
        map.put("NOT", "NOT");
        map.put("and", "AND");
        map.put("or", "OR");
        map.put("not", "NOT");
        return map;
    }

    private static String readFile(String fileName) {
        StringBuilder content = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            while ((line = br.readLine()) != null) {
                content.append(line).append("\n");
            }
        } catch (IOException e) {
            System.err.println("Error al leer el archivo: " + e.getMessage());
        }
        return content.toString();
    }
}

class Token {
    TokenType type;
    String value;
    String key;
    int row;
    int column;

    public Token(TokenType type, String value, String key, int row, int column) {
        this.type = type;
        this.value = value;
        this.key = key;
        this.row = row;
        this.column = column;
    }

    public String toString() {
        return key + "\t" + value + "\t" + row + "\t" + column;
    }
}

enum TokenType {
    NÚMERO,
    CADENA,
    PALABRA_RESERVADA,
    IDENTIFICADOR,
    SÍMBOLO,
    COMENTARIO_CORTO,
    COMENTARIO_LARGO,
    DESCONOCIDO
}
