<?php

## Riesenie prvej casti projektu z predmetu IPP 2022/2023
## Autor: Patrik Gafrik (xgafri00)


ini_set('display_errors', 'stderr');


$instructionOrder = 1;
$isVar = false;
$xml = new XMLWriter();
$xml->openUri("php://output");
$xml->startDocument('1.0', 'UTF-8');
$xml->setIndent(TRUE);
$xml->setIndentString("    ");

function tokenizeLine($line) {

    $tokens = array();
    $token = "";

    for ($i = 0; $i < strlen($line); $i++) {
        if ($line[$i] === " " || $line[$i] === "\t") {
            if ($token !== "") {
                $tokens[] = $token;
                $token = "";
            }
        } else {
            $token .= $line[$i];
        }
    }

    if ($token !== "") {
        $tokens[] = $token;
    }

    return $tokens;
}

function removeComment($item)
{
    $commentStart = strpos($item, '#');
    if ($commentStart !== false) {
        return substr($item, 0, $commentStart);
    }
    return $item;
}

function checkVar($var) {

    if (preg_match("/^(GF|LF|TF)@[a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*$/", $var)) {
          return true;
    }
    else {
        return false;
    }
}

function checkSymb($symb) {

    global $isVar;

    if (preg_match("/^int@[-+]?[0-9]+$/", $symb)) {
        $isVar = false;
        return array(true, $isVar);
    } elseif (preg_match("/^bool@(true|false)$/", $symb)) {
        $isVar = false;
        return array(true, $isVar);
    } elseif (preg_match("/^nil@nil$/", $symb)) {
        $isVar = false;
        return array(true, $isVar);
    } elseif (preg_match("/^string@(\\\\[0-9]{3}|[^#\\\\\s])*$/", $symb)) {
        $isVar = false;
        return array(true, $isVar);
    } elseif (checkVar($symb)) {
          $isVar = true;
        return array(true, $isVar);
    } else {
        return false;
    }
}

function checkLabel($label) {

    if (preg_match("/^[a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*$/", $label)) {
        return true;
    }
    else {
        return false;
    }
}

function checkType($type) {

    if (preg_match("/^(string|int|bool)$/", $type)) {
        return true;
    }
    else {
        return false;
    }
}

function writeInstruction($tokens) {

    global $instructionOrder, $xml;

    $xml->startElement('instruction');
    $xml->writeAttribute('order', $instructionOrder++);
    $xml->writeAttribute('opcode', strtoupper($tokens[0]));

}

function writeVar($token, $argNumber) {

    global $xml;
    $xml->startElement('arg'.$argNumber);
    $xml->writeAttribute('type', 'var');
    $xml->text($token);

}

function writeSymb($token, $argNumber) {

    global $xml;
    $const = explode('@', $token, 2);
    $xml->startElement('arg'.$argNumber);
    $xml->writeAttribute('type', $const[0]);
    $xml->text($const[1]);
}

function writeLabel($token, $argNumber) {

    global $xml;
    $xml->startElement('arg'.$argNumber);
    $xml->writeAttribute('type', 'label');
    $xml->text($token);
}

function writeType($token, $argNumber) {

    global $xml;
    $xml->startElement('arg'.$argNumber);
    $xml->writeAttribute('type', 'type');
    $xml->text($token);
}

function codeParse($tokens) {

    global $xml;

    switch(strtoupper($tokens[0])) {

        # no argument
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            if (count($tokens) > 1) {
                fwrite(STDERR, "Syntax error! Invalid number of arguments\n");
                exit(23);
            }
            writeInstruction($tokens);
            $xml->endElement();
            break;


        # <var>
        case "DEFVAR":
        case "POPS":
            if (count($tokens) !== 2 || !checkVar($tokens[1])) {
                exit(23);
            }
            writeInstruction($tokens);
            writeVar($tokens[1], 1);
            $xml->endElement();
            $xml->endElement();
            break;

        # <symb>
        case "PUSHS":
        case "WRITE":
        case "DPRINT":
        case "EXIT":
            if (count($tokens) !== 2) {
                exit(23);
            }
            $result = checkSymb($tokens[1]);
            if (!$result[0]) {
                exit(23);
            }
            writeInstruction($tokens);
            if ($result && !$result[1]) {
                writeSymb($tokens[1], 1);
                $xml->endElement();
            }
            else {
                writeVar($tokens[1], 1);
                $xml->endElement();
            }
            $xml->endElement();
            break;

        # <label>
        case "CALL":
        case "LABEL":
        case "JUMP":
            if (count($tokens) !== 2 || !checkLabel($tokens[1])) {
                exit(23);
            }
            writeInstruction($tokens);
            writeLabel($tokens[1], 1);
            $xml->endElement();
            $xml->endElement();
            break;

        # <var> <symb>
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "NOT":
        case "TYPE":
            if (count($tokens) !== 3) {
                exit(23);
            }
            $result = checkSymb($tokens[2]);
            if ((!checkVar($tokens[1]) || !($result[0]))) {
                exit(23);
            }

            writeInstruction($tokens);
            writeVar($tokens[1], 1);
            $xml->endElement();
            if ($result && !$result[1]) {
                writeSymb($tokens[2], 2);
                $xml->endElement();
            }
            else {
                writeVar($tokens[2], 2);
                $xml->endElement();
            }
            $xml->endElement();
            break;


        # <var> <symb> <symb>
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
              if (count($tokens) !== 4) {
                  exit(23);
              }
            $result1 = checkSymb($tokens[2]);
            $result2 = checkSymb($tokens[3]);
            if (
                !checkVar($tokens[1]) ||
                !$result1[0] ||
                !$result2[0]) {

                exit(23);
            }
            writeInstruction($tokens);
            writeVar($tokens[1], 1);
            $xml->endElement();
            if ($result1 && !$result1[1]) {
                writeSymb($tokens[2], 2);
                $xml->endElement();
            }
            else {
                writeVar($tokens[2], 2);
                $xml->endElement();
            }
            if ($result2 && !$result2[1]) {
                writeSymb($tokens[3], 3);
                $xml->endElement();
            }
            else {
                writeVar($tokens[3], 3);
                $xml->endElement();
            }
            $xml->endElement();
            break;


        # <var> <type>
        case "READ":
            if (count($tokens) !== 3 || !checkVar($tokens[1]) || !checkType($tokens[2])) {
                exit(23);
            }
            writeInstruction($tokens);
            writeVar($tokens[1], 1);
            $xml->endElement();
            writeType($tokens[2], 2);
            $xml->endElement();
            $xml->endElement();
            break;

        # <label> <symb> <symb>
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            if (count($tokens) !== 4) {
                exit(23);
            }
            $result1 = checkSymb($tokens[2]);
            $result2 = checkSymb($tokens[3]);
            if (
                !checkLabel($tokens[1]) ||
                !$result1[0] ||
                !$result2[0]) {

                exit(23);
            }
            writeInstruction($tokens);
            writeLabel($tokens[1], 1);
            $xml->endElement();
            if ($result1 && !$result1[1]) {
                writeSymb($tokens[2], 2);
                $xml->endElement();
            }
            else {
                writeVar($tokens[2], 2);
                $xml->endElement();
            }
            if ($result2 && !$result2[1]) {
                writeSymb($tokens[3], 3);
                $xml->endElement();
            }
            else {
                writeVar($tokens[3], 3);
                $xml->endElement();
            }
            $xml->endElement();
            break;

        default:
            exit(22);
    }
}

if ($argc == 2) {
    if ($argv[1] == "--help") {
        echo("Usage: php8.1 parser.php [options] <filename\n\n");
        exit(0);
    }
    else {
        fwrite(STDERR, "Invalid option, run 'parser.php --help' for usage info\n");
        exit(10);
    }
}

$headerPresence = false;

while($line = fgets(STDIN)) {

    # skips empty lines and comments
    if ($line == "\n" || $line[0] == '#') {
        continue;
    }

    $line = removeComment($line);
    $line = str_replace("\n", "", trim($line));
    $tokens = tokenizeLine($line);

    if (!$headerPresence) {
        if (preg_match("/^.ippcode23$/i", $line)) {
            $headerPresence = true;
            $xml->startElement("program");
            $xml->writeAttribute("language", "IPPcode23");
        }
        else {
            fwrite(STDERR, "Missing or invalid header!\n");
            exit(21);
        }
    }
    else {
        codeParse($tokens);
    }
}

$xml->endElement();
$xml->endDocument();

# writes xml to stdout
echo $xml->outputMemory();