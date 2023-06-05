"""
Reference:

Barista - Interpreter;

Recipe - class definition;
fragrance - class;
flavor - secondary class;
cuppa - object;
tea - new object/copy of class definition;
cup_of_the_day - main object;

Formula - template definition;

Instruction - method;
brew - object's method;
steep - copy of method;
recommended_brew - main object's method;
service - result of a method call;
order - result of a statement;

Tin - variable;
can - instantiated Tin;
bag - copy of variable;

Ingredient - boxed value;
beans - instantiated Ingredient;
milk - secondary instantiated Ingredient;
grounds - value;
cream - secondary value;
leaf - copy of field value;
roast - value after unary operation;
blend - value after binary operation;

Plate - stack frame;

Complaint - boxed exception;

bear - Brewin error;
rare - RuntimeError;
"""

from typing import Callable, Union, Tuple, Any
import copy
import sys
import pprint

from intbase import InterpreterBase, ErrorType
from bparser import BParser, StringWithLineNumber as SWLN


InputFun = Callable[[], str]
OutputFun = Callable[[str], None]
ErrorFun = Callable[[ErrorType, str, int], None]
BrewinTypes = Union[SWLN, int, str, bool, 'Recipe', None]
isSWLN = lambda token: isinstance(token, SWLN)
T2L = (lambda template: [SWLN(btype, template.line_num) for btype
                         in template.split(InterpreterBase.TYPE_CONCAT_CHAR)])
isVarType = (lambda token, me, classes:
             token in {InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF,
                       InterpreterBase.BOOL_DEF, me.name}.union(classes))
isMethodType = (lambda token, me, classes:
                token in {InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF,
                          InterpreterBase.BOOL_DEF, InterpreterBase.VOID_DEF,
                          me.name}.union(classes))
debug = lambda *values: print(*values, file=sys.stderr, flush=True)


class Barista(InterpreterBase):
    """
    Interpreter
    """
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    def run(self, program: list[str]):
        well_formed, tokens = BParser.parse(program)

        if not well_formed:
            super().error(ErrorType.SYNTAX_ERROR, tokens)

        if self.trace_output:
            debug("Line numbers:")
            pprint.pprint(tokens, stream=sys.stderr)
            debug()

        self.init()

        for class_def in tokens:
            match class_def:
                case [InterpreterBase.CLASS_DEF, name, *_] if isSWLN(name):
                    self.classes[name] = None
                case [InterpreterBase.TEMPLATE_CLASS_DEF, name, *_
                      ] if isSWLN(name):
                    self.templates[name] = None
                case _:
                    super().error(ErrorType.SYNTAX_ERROR,
                                  f"Not a class: {class_def}")

        for class_def in tokens:
            match class_def:
                case [InterpreterBase.CLASS_DEF, name,
                      InterpreterBase.INHERITS_DEF, parent_name,
                      *body] if isSWLN(name) and isSWLN(parent_name):
                    self.add_class(name, parent_name, body)
                case [InterpreterBase.CLASS_DEF, name, *body] if isSWLN(name):
                    self.add_class(name, None, body)
                case [InterpreterBase.TEMPLATE_CLASS_DEF, name, field_types,
                      *body] if isSWLN(name) and all(map(isSWLN, field_types)):
                    self.add_template(name, field_types, body)
                case _:
                    super().error(ErrorType.SYNTAX_ERROR,
                                  f"Not a class: {class_def}")

        if self.trace_output:
            debug("Parsed classes:")
            for recipe in self.classes.values():
                debug(f"  class {recipe.name}")
                debug("  fields:")
                for name, ingredient in recipe.fields.items():
                    debug(f"    {name}={ingredient.value}")
                debug("  methods:")
                for instruction in recipe.methods.values():
                    debug(f"    {instruction.name}({instruction.formals})=")
                    debug(f"{pprint.pformat(instruction.statement)}")
            debug("\nStarting execution...")

        try:
            cup_of_the_day = copy.copy(
                self.classes[InterpreterBase.MAIN_CLASS_DEF]
            )
        except KeyError:
            super().error(ErrorType.TYPE_ERROR, "Main class not found")

        try:
            cup_of_the_day.call_method(InterpreterBase.MAIN_FUNC_DEF,
                                       first_call=True, me=cup_of_the_day,
                                       exception=None)
        except KeyError:
            super().error(ErrorType.NAME_ERROR, "Main method not found",
                          cup_of_the_day.name.line_num)
        except ValueError:
            super().error(ErrorType.NAME_ERROR,
                          "Main method cannot accept arguments",
                          (cup_of_the_day.methods[InterpreterBase.MAIN_FUNC_DEF]
                           .name.line_num))
        except NameError as e:
            super().error(ErrorType.NAME_ERROR, str(e),
                          (cup_of_the_day.methods[InterpreterBase.MAIN_FUNC_DEF]
                           .name.line_num))
        except TypeError as e:
            super().error(ErrorType.TYPE_ERROR, str(e),
                          (cup_of_the_day.methods[InterpreterBase.MAIN_FUNC_DEF]
                           .name.line_num))

    def init(self):
        self.classes: dict[SWLN, Recipe | None] = {}
        self.templates: dict[SWLN, Formula | None] = {}

    def add_class(self, name: SWLN, parent_name: SWLN | None, body: list):
        if name in self.classes and self.classes[name]:
            super().error(ErrorType.TYPE_ERROR, f"Duplicate classes: {name}",
                          name.line_num)
        self.classes[name] = Recipe(name, parent_name, body, self.classes,
                                    self.templates, super().get_input,
                                    super().output, super().error,
                                    self.trace_output)

    def add_template(self, name: SWLN, field_types: list[SWLN], body: list):
        if name in self.templates and self.templates[name]:
            super().error(ErrorType.TYPE_ERROR, f"Duplicate templates: {name}",
                          name.line_num)
        self.templates[name] = Formula(name, field_types, body, self.classes,
                                       self.templates, super().get_input,
                                       super().output, super().error,
                                       self.trace_output)


class Ingredient:
    """
    Field definition
    """
    def __init__(self, value: BrewinTypes, error: ErrorFun,
                 trace_output: bool) -> None:
        """
        Throws ValueError on invalid value
        """
        self.error = error
        self.trace_output = trace_output
        self.btype = None
        self.is_super = False

        match value:
            case grounds if not isSWLN(grounds):
                if self.trace_output:
                    debug(f"Raw value to Ingredient: {grounds}:{type(grounds)}")
                self.value = value
            case InterpreterBase.NULL_DEF:
                self.value = None
            case InterpreterBase.TRUE_DEF:
                self.value = True
            case InterpreterBase.FALSE_DEF:
                self.value = False
            case str_or_int:
                try:
                    if str_or_int[0] == '"' and str_or_int[-1] == '"':
                        self.value = str_or_int[1:-1]
                    else:
                        self.value = int(str_or_int)
                except IndexError:
                    self.error(ErrorType.SYNTAX_ERROR, "Blank value, somehow",
                               value.line_num)

    def __str__(self) -> str:
        match self.value:
            case True:
                return InterpreterBase.TRUE_DEF
            case False:
                return InterpreterBase.FALSE_DEF
            case None:
                return InterpreterBase.NULL_DEF
        return str(self.value)


class Recipe:
    """
    Class definition
    """
    def __init__(self, name: SWLN, parent_name: SWLN | None, body: list,
                 classes: dict[SWLN, 'Recipe'],
                 templates: dict[SWLN, 'Formula'], get_input: InputFun,
                 output: OutputFun, error: ErrorFun, trace_output: bool
                 ) -> None:
        self.name = name
        self.classes = classes
        self.templates = templates
        self.get_input = get_input
        self.output = output
        self.error = error
        self.trace_output = trace_output
        self.fields: dict[SWLN, Tin] = {}
        self.methods: dict[SWLN, Instruction] = {}

        if parent_name:
            try:
                self.parent = copy.copy(classes[parent_name])
            except KeyError:
                self.error(ErrorType.TYPE_ERROR,
                           f"Class {parent_name} not defined above",
                           parent_name.line_num)
        else:
            self.parent = None

        for definition in body:
            match definition:
                case [InterpreterBase.FIELD_DEF, btype, name, value
                      ] if isSWLN(btype) and isSWLN(name) and isSWLN(value):
                    self.add_field(name, btype, value)
                case [InterpreterBase.FIELD_DEF, btype, name
                      ] if isSWLN(btype) and isSWLN(name):
                    temp_name, *types = T2L(btype)
                    match btype:
                        case InterpreterBase.INT_DEF:
                            self.add_field(name, btype, 0)
                        case InterpreterBase.STRING_DEF:
                            self.add_field(name, btype, "")
                        case InterpreterBase.BOOL_DEF:
                            self.add_field(name, btype, False)
                        case class_name if isVarType(class_name, self,
                                                     self.classes):
                            self.add_field(name, btype, None)
                        case class_name if temp_name in self.templates:
                            try:
                                self.templates[temp_name].compile(*types)
                            except ValueError:
                                self.error(ErrorType.TYPE_ERROR,
                                           f"Template created with wrong "
                                           f"number of types: {temp_name}",
                                           temp_name.line_num)
                            self.add_field(name, btype, None)
                        case _:
                            self.error(ErrorType.TYPE_ERROR,
                                       f"Class {btype} not defined above",
                                       btype.line_num)
                case [InterpreterBase.METHOD_DEF, btype, name, params,
                      statement, *_] if isSWLN(btype) and isSWLN(name):
                    self.add_method(name, btype, params, statement)
                case _:
                    self.error(ErrorType.SYNTAX_ERROR,
                               f"Not a field or method: {definition}")

    def __copy__(self):
        tea = Recipe(self.name, self.parent.name if self.parent else None, [],
                     self.classes, self.templates, self.get_input, self.output,
                     self.error, self.trace_output)
        for name, bag in self.fields.items():
            tea.add_field(name, bag.btype, bag.value.value)
        for steep in self.methods.values():
            tea.add_method(steep.name, steep.btype, steep.formals,
                           steep.statement)
        return tea

    def __str__(self) -> str:
        return f'<class {self.name}>'

    def add_field(self, name: SWLN, btype: SWLN, value: BrewinTypes):
        if name in self.fields:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate fields in {self.name}: {name}",
                       name.line_num)
        try:
            beans = Ingredient(value, self.error, self.trace_output)
        except ValueError:
            self.error(ErrorType.SYNTAX_ERROR, f"Not a valid value: {value}",
                       value.line_num)
        try:
            self.fields[name] = Tin(name, btype, beans, self, self.classes,
                                    self.templates, self.error,
                                    self.trace_output)
        except TypeError as e:
            self.error(ErrorType.TYPE_ERROR, str(e), value.line_num)

    def add_method(self, name: SWLN, btype: SWLN,
                   params: dict[SWLN, SWLN] | Any, statement):
        if name in self.methods:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate methods in {self.name}: {name}",
                       name.line_num)
        self.methods[name] = Instruction(name, btype, params, statement, self,
                                         self.classes, self.templates,
                                         self.fields, self.get_input,
                                         self.output, self.error,
                                         self.trace_output)

    def is_instance(self, class_name: SWLN) -> bool:
        return (self.name == class_name
                or (self.parent and self.parent.is_instance(class_name)))

    def call_method(self, name: SWLN, *args: Ingredient, first_call: bool,
                    me: 'Recipe', exception: Ingredient | None
                    ) -> Ingredient | None:
        """
        Throws KeyError if method not found

        Throws ValueError on wrong number of arguments

        Throws NameError on wrong type passed in

        Throws TypeError on wrong type returned
        """
        if self.trace_output and first_call:
            debug(f"First call, setting me={self.name}")
        if self.parent:
            try:
                return self.methods[name].call(*args,
                                               me=self if first_call else me,
                                               exception=exception)
            except (KeyError, ValueError, NameError, TypeError):
                pass
            return self.parent.call_method(name, *args, first_call=False,
                                           me=self if first_call else me,
                                           exception=exception)
        else:
            return self.methods[name].call(*args, me=self if first_call else me,
                                           exception=exception)


class Formula():
    """
    Template definition
    """
    def __init__(self, name: SWLN, field_types: list[SWLN], body: list,
                 classes: dict[SWLN, Recipe], templates: dict[SWLN, 'Formula'],
                 get_input: InputFun, output: OutputFun, error: ErrorFun,
                 trace_output: bool) -> None:
        self.name = name
        self.field_types = field_types
        self.body = body
        self.classes = classes
        self.templates = templates
        self.get_input = get_input
        self.output = output
        self.error = error
        self.trace_output = trace_output

    def substitute_types(self, body, type_map: dict[SWLN, SWLN]):
        if isSWLN(body):
            if body in type_map:
                return type_map[body]
            elif len(l := T2L(body)) > 1:
                return SWLN(
                    InterpreterBase.TYPE_CONCAT_CHAR.join(
                        self.substitute_types(t, type_map) for t in l
                    ),
                    body.line_num
                )
            else:
                return body
        return [ self.substitute_types(part, type_map) for part in body ]

    def compile(self, *types: SWLN) -> Recipe:
        """
        Throws ValueError on wrong number of types
        """
        name = SWLN(InterpreterBase.TYPE_CONCAT_CHAR.join([self.name, *types]),
                    self.name.line_num)
        if name in self.classes:
            return self.classes[name]
        if self.trace_output:
            debug(f"Compiling {name}")
        if self.trace_output:
            debug(f"{self.name} got {types=}")
        for btype in types:
            if self.trace_output:
                debug(f"{self.name} got type {btype}")
            if not isVarType(btype, self, self.classes):
                self.error(ErrorType.TYPE_ERROR,
                           f"Class {btype} not defined above", btype.line_num)
        type_map = {field_type: btype for field_type, btype
                    in zip(self.field_types, types, strict=True)}
        if self.trace_output:
            debug(f"{self.name}@{'@'.join(types)} type map: {type_map}")
        body = self.substitute_types(self.body, type_map)
        if self.trace_output:
            debug(f"Body parsed from {self.name}@{'@'.join(types)}:")
            debug(pprint.pformat(body))
        cuppa = Recipe(name, None, body, self.classes, self.templates,
                       self.get_input, self.output, self.error,
                       self.trace_output)
        self.classes[name] = cuppa
        return cuppa


class Tin:
    """
    Variable definition
    """
    def __init__(self, name: SWLN, btype: SWLN, boxed_value: Ingredient,
                 me: Recipe, classes: dict[SWLN, Recipe],
                 templates: dict[SWLN, Formula], error: ErrorFun,
                 trace_output: bool) -> None:
        """
        Throws TypeError on incompatible type
        """
        self.name = name
        self.classes = classes
        self.templates = templates
        self.error = error
        self.trace_output = trace_output

        temp_name, *types = T2L(btype)

        if self.trace_output:
            debug(f"Tin checking {btype=}")

        if isVarType(btype, me, classes):
            self.btype = btype
        elif temp_name in templates:
            try:
                templates[temp_name].compile(*types)
                if self.trace_output:
                    debug(f"Tin compiled {btype=}")
            except ValueError:
                self.error(ErrorType.TYPE_ERROR,
                           f"Template created with wrong number of types: "
                           f"{temp_name}",
                           temp_name.line_num)
            self.btype = btype
        else:
            self.error(ErrorType.TYPE_ERROR, f"Class {btype} not defined above",
                       btype.line_num)

        if self.trace_output:
            debug(f"Tin {self.name} declared {self.btype}")

        self.set_value(boxed_value)

    def set_value(self, boxed_value: Ingredient):
        """
        Throws TypeError on incompatible type
        """
        grounds = boxed_value.value
        if self.trace_output:
            debug(f"Setting {self.btype=} var to {type(grounds)=}")
        match self.btype:
            case InterpreterBase.INT_DEF:
                if type(grounds) == int:
                    boxed_value.btype = self.btype
                    self.value = boxed_value
                    return
            case InterpreterBase.STRING_DEF:
                if type(grounds) == str:
                    boxed_value.btype = self.btype
                    self.value = boxed_value
                    return
            case InterpreterBase.BOOL_DEF:
                if type(grounds) == bool:
                    boxed_value.btype = self.btype
                    self.value = boxed_value
                    return
            case class_name:
                if grounds is None:
                    if (boxed_value.btype and boxed_value.btype in self.classes
                        and not self.classes[boxed_value.btype]
                                    .is_instance(self.btype)):
                        raise TypeError(f"Class {boxed_value.btype} not "
                                        f"derived from {class_name}")
                    boxed_value.btype = self.btype
                    self.value = boxed_value
                    return
                try:
                    if grounds.is_instance(class_name):
                        boxed_value.btype = self.btype
                        self.value = boxed_value
                        return
                    raise TypeError(f"Class {grounds.name} not derived from "
                                    f"{class_name}")
                except AttributeError:
                    pass
        match grounds:
            case int():
                raise TypeError(f"Cannot assign value of type "
                                f"{InterpreterBase.INT_DEF} to variable of "
                                f"type {self.btype}")
            case str():
                raise TypeError(f"Cannot assign value of type "
                                f"{InterpreterBase.STRING_DEF} to variable of "
                                f"type {self.btype}")
            case bool():
                raise TypeError(f"Cannot assign value of type "
                                f"{InterpreterBase.BOOL_DEF} to variable of "
                                f"type {self.btype}")
            case _:
                raise TypeError(f"Cannot assign object to variable of type "
                                f"{self.btype}")


class Instruction:
    """
    Method definition
    """
    def __init__(self, name: SWLN, btype: SWLN, params: dict[SWLN, SWLN] | Any,
                 statement, me: Recipe, classes: dict[SWLN, Recipe],
                 templates: dict[SWLN, Formula], fields: dict[SWLN, Tin],
                 get_input: InputFun, output: OutputFun, error: ErrorFun,
                 trace_output: bool) -> None:
        self.name = name
        self.statement = statement
        self.me = me
        self.classes = classes
        self.templates = templates
        self.fields = fields
        self.get_input = get_input
        self.output = output
        self.error = error
        self.trace_output = trace_output
        self.formals: dict[SWLN, SWLN] = {}

        temp_name, *types = T2L(btype)

        if isMethodType(btype, me, classes):
            self.btype = btype
        elif temp_name in templates:
            try:
                templates[temp_name].compile(*types)
            except ValueError:
                self.error(ErrorType.TYPE_ERROR,
                           f"Template created with wrong number of types: "
                           f"{temp_name}",
                           temp_name.line_num)
            self.btype = btype
        else:
            self.error(ErrorType.TYPE_ERROR, f"Class {btype} not defined above",
                       btype.line_num)

        if type(params) == dict:
            self.formals = params
        else:
            for param in params:
                match param:
                    case [btype, formal] if isSWLN(btype) and isSWLN(formal):
                        self.add_parameter(formal, btype)
                    case _:
                        error(ErrorType.SYNTAX_ERROR,
                              f"Malformed parameter: {param}", name.line_num)

    def call(self, *args: Ingredient, me: Recipe, exception: Ingredient | None
             ) -> Ingredient | None:
        """
        Throws ValueError on wrong number of arguments

        Throws NameError on wrong type passed in

        Throws TypeError on wrong type returned
        """
        try:
            parameters = {formal: Tin(formal, btype, actual, me,
                                      self.classes, self.templates, self.error,
                                      self.trace_output)
                          for (formal, btype), actual
                          in zip(self.formals.items(), args, strict=True)}
        except TypeError as e:
            raise NameError(str(e))

        is_return, beans = evaluate_statement(self.statement, me,
                                              self.me.parent, self.classes,
                                              self.templates, exception, None,
                                              parameters, self.fields,
                                              self.get_input, self.output,
                                              self.error, self.trace_output)
        if is_return and beans:
            grounds = beans.value
            if self.trace_output:
                debug(f"Returning {type(grounds)=} val from {self.btype=}")
            match self.btype:
                case InterpreterBase.INT_DEF:
                    if type(grounds) == int:
                        beans.btype = self.btype
                        return beans
                case InterpreterBase.STRING_DEF:
                    if type(grounds) == str:
                        beans.btype = self.btype
                        return beans
                case InterpreterBase.BOOL_DEF:
                    if type(grounds) == bool:
                        beans.btype = self.btype
                        return beans
                case InterpreterBase.VOID_DEF:
                    raise TypeError(f"Cannot return any value from method of "
                                    f"type {InterpreterBase.VOID_DEF}")
                case class_name:
                    if grounds is None:
                        if (beans.btype and beans.btype in self.classes
                            and not self.classes[beans.btype]
                                        .is_instance(self.btype)):
                            raise TypeError(f"Class {beans.btype} not derived "
                                            f"from {class_name}")
                        beans.btype = self.btype
                        return beans
                    try:
                        if grounds.is_instance(class_name):
                            beans.btype = self.btype
                            return beans
                        raise TypeError(f"Returned object class {grounds.name} "
                                        f"not derived from {class_name}")
                    except AttributeError:
                        pass
            match grounds:
                case int():
                    raise TypeError(f"Cannot return value of type "
                                    f"{InterpreterBase.INT_DEF} from method of "
                                    f"type {self.btype}")
                case str():
                    raise TypeError(f"Cannot return value of type "
                                    f"{InterpreterBase.STRING_DEF} from method "
                                    f"of type {self.btype}")
                case bool():
                    raise TypeError(f"Cannot return value of type "
                                    f"{InterpreterBase.BOOL_DEF} from method "
                                    f"of type {self.btype}")
                case _:
                    raise TypeError(f"Cannot return object from method of type "
                                    f"{self.btype}")

        match self.btype:
            case InterpreterBase.INT_DEF:
                beans = Ingredient(0, self.error, self.trace_output)
                beans.btype = self.btype
                return beans
            case InterpreterBase.STRING_DEF:
                beans = Ingredient("", self.error, self.trace_output)
                beans.btype = self.btype
                return beans
            case InterpreterBase.BOOL_DEF:
                beans = Ingredient(False, self.error, self.trace_output)
                beans.btype = self.btype
                return beans
            case InterpreterBase.VOID_DEF:
                return None
            case class_name:
                beans = Ingredient(None, self.error, self.trace_output)
                beans.btype = self.btype
                return beans

    def add_parameter(self, name: SWLN, btype: SWLN):
        if name in self.formals:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate parameters in {self.name}: name",
                       name.line_num)
        temp_name, *types = T2L(btype)
        if isVarType(btype, self.me, self.classes):
            self.formals[name] = btype
        elif temp_name in self.templates:
            try:
                self.templates[temp_name].compile(*types)
            except ValueError:
                self.error(ErrorType.TYPE_ERROR,
                           f"Template created with wrong number of types: "
                           f"{temp_name}",
                           temp_name.line_num)
            self.formals[name] = btype
        else:
            self.error(ErrorType.TYPE_ERROR, f"Class {btype} not defined above",
                       btype.line_num)


class Plate:
    """
    Stack frame
    """
    def __init__(self, stack: Union['Plate', None], me: Recipe,
                 classes: dict[SWLN, Recipe], templates: dict[SWLN, Formula],
                 error: ErrorFun, trace_output: bool) -> None:
        self.under = stack
        self.me = me
        self.classes = classes
        self.templates = templates
        self.error = error
        self.trace_output = trace_output
        self.locals: dict[SWLN, Tin] = {}

    def add_variable(self, name: SWLN, btype: SWLN, value: BrewinTypes):
        if self.trace_output:
            debug(f"Plate {value}")
        if name in self.locals:
            self.error(ErrorType.NAME_ERROR,
                       f"Duplicate local variable: {name}", name.line_num)
        try:
            beans = Ingredient(value, self.error, self.trace_output)
            if self.trace_output:
                debug(f"Prepped {beans}")
        except ValueError:
            self.error(ErrorType.SYNTAX_ERROR, f"Not a valid value: {value}",
                       name.line_num)
        try:
            self.locals[name] = Tin(name, btype, beans, self.me, self.classes,
                                    self.templates, self.error,
                                    self.trace_output)
            if self.trace_output:
                debug(f"Plated {self.locals[name]}")
        except TypeError as e:
            self.error(ErrorType.TYPE_ERROR, str(e), btype.line_num)

    def get_variable(self, name: SWLN) -> Tin | None:
        if self.trace_output:
            debug(f"Tracing stack: finding {name}")
        if name in self.locals:
            return self.locals[name]
        if self.trace_output:
            debug(f"{name} not found in {self}")
        if self.under:
            return self.under.get_variable(name)
        if self.trace_output:
            debug(f"{name} is bottom plate")
        return None


class Complaint(Exception):
    """
    Exception
    """
    def __init__(self, message: Ingredient) -> None:
        """
        Throws ValueError if message is not of type string
        """
        if type(message.value) != str:
            raise ValueError(f"Non-string used as exception: {message}")

        super().__init__(str(message))

        self.message = message

    def __str__(self) -> str:
        return str(self.message)


def evaluate_expression(expression, me: Recipe, super: Recipe | None,
                        classes: dict[SWLN, Recipe],
                        templates: dict[SWLN, Formula],
                        exception: Ingredient | None, stack: Plate | None,
                        parameters: dict[SWLN, Tin], fields: dict[SWLN, Tin],
                        error: ErrorFun, trace_output: bool) -> Ingredient:
    """
    Guaranteed to return a boxed value (or throw a Brewin error if unable to)
    """
    if trace_output:
        if type(expression) == list:
            try:
                debug(f"line {expression[0].line_num}: Expression starts with "
                    f"{expression[0]}")
            except IndexError:
                debug("Empty expression")
            except AttributeError:
                debug(f"no line_num: Expression starts with {expression[0]}")
        else:
            try:
                debug(f"line {expression.line_num}: Expression is {expression}")
            except AttributeError:
                debug(f"no line_num: Expression is {expression}")
    match expression:
        case InterpreterBase.ME_DEF:
            return Ingredient(me, error, trace_output)
        case InterpreterBase.SUPER_DEF:
            if super:
                beans = Ingredient(super, error, trace_output)
                beans.is_super = True
                return beans
            else:
                error(ErrorType.TYPE_ERROR, "Class is not inherited",
                      expression.line_num)
        case InterpreterBase.EXCEPTION_VARIABLE_DEF:
            if exception:
                return exception
            else:
                error(ErrorType.NAME_ERROR, "No exception has been thrown yet",
                      expression.line_num)
        case variable if (isSWLN(variable) and stack
                          and (can := stack.get_variable(variable))):
            return can.value
        case variable if isSWLN(variable) and variable in parameters:
            return parameters[variable].value
        case variable if isSWLN(variable) and variable in fields:
            return fields[variable].value
        case const if isSWLN(const):
            try:
                return Ingredient(const, error, trace_output)
            except ValueError:
                error(ErrorType.NAME_ERROR, f"Variable not found: {const}",
                      const.line_num)
        case [InterpreterBase.CALL_DEF, obj_expression, method, *arguments
              ] if isSWLN(method):
            beans = evaluate_expression(obj_expression, me, super, classes,
                                        templates, exception, stack, parameters,
                                        fields, error, trace_output)
            cuppa = beans.value
            if cuppa is None:
                error(ErrorType.FAULT_ERROR,
                      f"Trying to dereference nullptr", expression[0].line_num)
            try:
                service = cuppa.call_method(
                    method,
                    *(evaluate_expression(argument, me, super, classes,
                                          templates, exception, stack,
                                          parameters, fields, error,
                                          trace_output)
                      for argument in arguments),
                    first_call=not beans.is_super,
                    me=me,
                    exception=exception
                )
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Object does not have method: {method}", method.line_num)
            except AttributeError:
                error(ErrorType.TYPE_ERROR,
                      f"Method being called on non-object",
                      expression[0].line_num)
            except ValueError:
                error(ErrorType.NAME_ERROR,
                      f"Method called with wrong number of arguments: {method}",
                      expression[0].line_num)
            except NameError as e:
                error(ErrorType.NAME_ERROR, str(e), expression[0].line_num)
            except TypeError as e:
                error(ErrorType.TYPE_ERROR, str(e), expression[0].line_num)
            if service is None:
                error(ErrorType.TYPE_ERROR,
                      f"Method did not return a value: {method}",
                      expression[0].line_num)
            else:
                return service
        case [InterpreterBase.NEW_DEF, name] if isSWLN(name):
            name, *types = T2L(name)
            if trace_output:
                debug(f"New with {name=}, {types=}")
            if types:
                try:
                    cuppa = templates[name].compile(*types)
                except KeyError:
                    error(ErrorType.TYPE_ERROR,
                          f"Could not find template: {name}",
                          expression[0].line_num)
                except ValueError:
                    error(ErrorType.TYPE_ERROR,
                          f"Template created with wrong number of types: "
                          f"{name}",
                          name.line_num)
            else:
                try:
                    cuppa = classes[name]
                except KeyError:
                    error(ErrorType.TYPE_ERROR, f"Could not find class: {name}",
                          expression[0].line_num)
            if trace_output:
                debug(f"Object {cuppa} generated")
            return Ingredient(copy.copy(cuppa), error, trace_output)
        case [unary_operator, sub_expression] if isSWLN(unary_operator):
            grounds = evaluate_expression(sub_expression, me, super, classes,
                                          templates, exception, stack,
                                          parameters, fields, error,
                                          trace_output).value
            if trace_output:
                debug(f"{unary_operator=} with {grounds=}:{type(grounds)}")
            match unary_operator:
                case '!' if type(grounds) == bool:
                    roast = bool(not grounds)
                case _:
                    error(ErrorType.TYPE_ERROR,
                        f"No use of {unary_operator} is compatible with "
                        f"expression type: {type(grounds)}",
                        unary_operator.line_num)
            if trace_output:
                debug(f"{type(roast)=}")
            return Ingredient(roast, error, trace_output)
        case [binary_operator, left_expression, right_expression
              ] if isSWLN(binary_operator):
            beans = evaluate_expression(left_expression, me, super, classes,
                                        templates, exception, stack, parameters,
                                        fields, error, trace_output)
            grounds = beans.value
            milk = evaluate_expression(right_expression, me, super, classes,
                                       templates, exception, stack, parameters,
                                       fields, error, trace_output)
            cream = milk.value
            if trace_output:
                debug(f"{binary_operator=} with {grounds=}:{type(grounds)} and "
                      f"{cream=}:{type(cream)}")
            match binary_operator:
                # NOTE: `eval` only used after operator becomes known to prevent
                #       arbitrary code execution
                case '+'|'-'|'*'|'/'|'%' if type(grounds) == type(cream) == int:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = int(operator(grounds, cream))
                case '<'|'>'|'<='|'>='|'!='|'==' \
                        if type(grounds) == type(cream) == int:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = bool(operator(grounds, cream))
                case '+' if type(grounds) == type(cream) == str:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = str(operator(grounds, cream))
                case '=='|'!='|'<'|'>'|'<='|'>=' \
                        if type(grounds) == type(cream) == str:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = bool(operator(grounds, cream))
                case '!='|'==' if type(grounds) == type(cream) == bool:
                    operator = eval(
                        f'lambda left, right: left {binary_operator} right'
                    )
                    blend = bool(operator(grounds, cream))
                case '&' if type(grounds) == type(cream) == bool:
                    blend = bool(grounds and cream)
                case '|' if type(grounds) == type(cream) == bool:
                    blend = bool(grounds or cream)
                case '==' if ((grounds is None or isinstance(grounds, Recipe))
                              and (cream is None or isinstance(cream, Recipe))):
                    if beans.btype:
                        fragrance = classes[beans.btype]
                    else:
                        fragrance = grounds
                    if milk.btype:
                        flavor = classes[milk.btype]
                    else:
                        flavor = milk
                    try:
                        if not (fragrance.is_instance(flavor.name)
                                or flavor.is_instance(fragrance.name)):
                            error(ErrorType.TYPE_ERROR,
                                  f"Classes {fragrance.name} and {flavor.name} "
                                  f"are not related",
                                  binary_operator.line_num)
                    except AttributeError:
                        pass
                    blend = bool(grounds is cream)
                case '!=' if ((grounds is None or isinstance(grounds, Recipe))
                              and (cream is None or isinstance(cream, Recipe))):
                    if beans.btype:
                        fragrance = classes[beans.btype]
                    else:
                        fragrance = grounds
                    if milk.btype:
                        flavor = classes[milk.btype]
                    else:
                        flavor = milk
                    try:
                        if not (fragrance.is_instance(flavor.name)
                                or flavor.is_instance(fragrance.name)):
                            error(ErrorType.TYPE_ERROR,
                                  f"Classes {fragrance.name} and {flavor.name} "
                                  f"are not related",
                                  binary_operator.line_num)
                    except AttributeError:
                        pass
                    blend = bool(grounds is not cream)
                case _:
                    error(ErrorType.TYPE_ERROR,
                        f"No use of {binary_operator} is compatible with "
                        f"expression types: {type(grounds)}, {type(cream)}",
                        binary_operator.line_num)
            if trace_output:
                debug(f"{type(blend)=}")
            return Ingredient(blend, error, trace_output)
        case _:
            error(ErrorType.SYNTAX_ERROR,
                  f"Not a valid expression: {expression}")


def evaluate_statement(statement, me: Recipe, super: Recipe | None,
                       classes: dict[SWLN, Recipe],
                       templates: dict[SWLN, Formula],
                       exception: Ingredient | None, stack: Plate | None,
                       parameters: dict[SWLN, Tin], fields: dict[SWLN, Tin],
                       get_input: InputFun, output: OutputFun, error: ErrorFun,
                       trace_output: bool) -> Tuple[bool, None | Ingredient]:
    """
    Returns a tuple of the form (<if the method is returning>, <the boxed value
    of the return, if there is one>)
    """
    if trace_output:
        try:
            debug(f"line {statement[0].line_num}: Running {statement[0]}")
        except IndexError:
            debug("Empty statement")
        except AttributeError:
            debug(f"no line_num: Running {statement[0]}")
    match statement:
        case [InterpreterBase.BEGIN_DEF, *sub_statements] if sub_statements:
            for sub_statement in sub_statements:
                latest_order = evaluate_statement(sub_statement, me, super,
                                                  classes, templates, exception,
                                                  stack, parameters, fields,
                                                  get_input, output, error,
                                                  trace_output)
                if latest_order[0]:
                    return latest_order
        case [InterpreterBase.CALL_DEF, expression, method, *arguments
              ] if isSWLN(method):
            beans = evaluate_expression(expression, me, super, classes,
                                        templates, exception, stack, parameters,
                                        fields, error, trace_output)
            cuppa = beans.value
            if cuppa is None:
                error(ErrorType.FAULT_ERROR,
                      f"Trying to dereference nullptr", statement[0].line_num)
            try:
                cuppa.call_method(
                    method,
                    *(evaluate_expression(argument, me, super, classes,
                                          templates, exception, stack,
                                          parameters, fields, error,
                                          trace_output)
                      for argument in arguments),
                    first_call=not beans.is_super,
                    me=me,
                    exception=exception
                )
            except KeyError:
                error(ErrorType.NAME_ERROR,
                      f"Object does not have method: {method}", method.line_num)
            except AttributeError:
                error(ErrorType.TYPE_ERROR,
                      f"Method being called on non-object",
                      statement[0].line_num)
            except ValueError:
                error(ErrorType.NAME_ERROR,
                      f"Method called with wrong number of arguments: {method}",
                      statement[0].line_num)
            except NameError as e:
                error(ErrorType.NAME_ERROR, str(e), statement[0].line_num)
            except TypeError as e:
                error(ErrorType.TYPE_ERROR, str(e), statement[0].line_num)
        case [InterpreterBase.IF_DEF, expression, true_statement]:
            condition = evaluate_expression(expression, me, super, classes,
                                            templates, exception, stack,
                                            parameters, fields, error,
                                            trace_output).value
            if type(condition) != bool:
                error(ErrorType.TYPE_ERROR,
                      "Condition did not evaluate to boolean",
                      statement[0].line_num)
            if condition:
                order = evaluate_statement(true_statement, me, super, classes,
                                           templates, exception, stack,
                                           parameters, fields, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
        case [InterpreterBase.IF_DEF, expression, true_statement,
              false_statement]:
            condition = evaluate_expression(expression, me, super, classes,
                                            templates, exception, stack,
                                            parameters, fields, error,
                                            trace_output).value
            if type(condition) != bool:
                error(ErrorType.TYPE_ERROR,
                      "Condition did not evaluate to boolean",
                      statement[0].line_num)
            if condition:
                order = evaluate_statement(true_statement, me, super, classes,
                                           templates, exception, stack,
                                           parameters, fields, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
            else:
                order = evaluate_statement(false_statement, me, super, classes,
                                           templates, exception, stack,
                                           parameters, fields, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
        case [InterpreterBase.INPUT_INT_DEF, variable] if isSWLN(variable):
            if stack and (can := stack.get_variable(variable)):
                pass
            elif variable in parameters:
                can = parameters[variable]
            elif variable in fields:
                can = fields[variable]
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
            try:
                beans = Ingredient(int(get_input()), error, trace_output)
            except ValueError:
                error(ErrorType.TYPE_ERROR,
                        "Could not convert input to integer",
                        statement[0].line_num)
            except TypeError:
                error(ErrorType.TYPE_ERROR, "Expected input but got none",
                        statement[0].line_num)
            try:
                can.set_value(beans)
            except TypeError as e:
                error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
        case [InterpreterBase.INPUT_STRING_DEF, variable] if isSWLN(variable):
            if stack and (can := stack.get_variable(variable)):
                pass
            elif variable in parameters:
                can = parameters[variable]
            elif variable in fields:
                can = fields[variable]
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
            beans = Ingredient(str(get_input()), error, trace_output)
            try:
                can.set_value(beans)
            except TypeError as e:
                error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
        case [InterpreterBase.PRINT_DEF, *arguments]:
            if trace_output:
                debug(output)
            output(
                ''.join(
                    str(
                        evaluate_expression(argument, me, super, classes,
                                            templates, exception, stack,
                                            parameters, fields, error,
                                            trace_output)
                    )
                    for argument in arguments
                )
            )
        case [InterpreterBase.RETURN_DEF]:
            return True, None
        case [InterpreterBase.RETURN_DEF, expression]:
            return True, evaluate_expression(expression, me, super, classes,
                                             templates, exception, stack,
                                             parameters, fields, error,
                                             trace_output)
        case [InterpreterBase.SET_DEF, variable, expression
              ] if isSWLN(variable):
            if stack and (can := stack.get_variable(variable)):
                pass
            elif variable in parameters:
                can = parameters[variable]
            elif variable in fields:
                can = fields[variable]
            else:
                error(ErrorType.NAME_ERROR, f"Variable not found: {variable}",
                      variable.line_num)
            beans = evaluate_expression(expression, me, super, classes,
                                        templates, exception, stack, parameters,
                                        fields, error, trace_output)
            try:
                can.set_value(beans)
            except TypeError as e:
                error(ErrorType.TYPE_ERROR, str(e), variable.line_num)
        case [InterpreterBase.WHILE_DEF, expression, statement_to_run]:
            while True:
                condition = evaluate_expression(expression, me, super, classes,
                                                templates, exception, stack,
                                                parameters, fields, error,
                                                trace_output).value
                if type(condition) != bool:
                    error(ErrorType.TYPE_ERROR,
                          "Condition did not evaluate to boolean",
                          statement[0].line_num)
                if not condition:
                    break
                latest_order = evaluate_statement(statement_to_run, me, super,
                                                  classes, templates, exception,
                                                  stack, parameters, fields,
                                                  get_input, output, error,
                                                  trace_output)
                if latest_order[0]:
                    return latest_order
        case [InterpreterBase.LET_DEF, var_defs, *sub_statements
              ] if sub_statements:
            stack = Plate(stack, me, classes, templates, error, trace_output)
            for var_def in var_defs:
                if trace_output:
                    debug(f"Let {var_def=}")
                match var_def:
                    case [btype, name, value] if (isSWLN(btype) and isSWLN(name)
                                                  and isSWLN(value)):
                        stack.add_variable(name, btype, value)
                    case [btype, name] if isSWLN(btype) and isSWLN(name):
                        temp_name, *types = T2L(btype)
                        match btype:
                            case InterpreterBase.INT_DEF:
                                stack.add_variable(name, btype, 0)
                            case InterpreterBase.STRING_DEF:
                                stack.add_variable(name, btype, "")
                            case InterpreterBase.BOOL_DEF:
                                stack.add_variable(name, btype, False)
                            case class_name if isVarType(class_name, me,
                                                         classes):
                                stack.add_variable(name, btype, None)
                            case class_name if temp_name in templates:
                                try:
                                    templates[temp_name].compile(*types)
                                except ValueError:
                                    error(ErrorType.TYPE_ERROR,
                                          f"Template created with wrong number "
                                          f"of types: {temp_name}",
                                          temp_name.line_num)
                                stack.add_variable(name, btype, None)
                            case _:
                                error(ErrorType.TYPE_ERROR,
                                      f"Class {btype} not defined above",
                                      btype.line_num)
                    case _:
                        error(ErrorType.SYNTAX_ERROR,
                              f"Malformed local variable: {var_def}",
                              statement[0].line_num)
            for sub_statement in sub_statements:
                latest_order = evaluate_statement(sub_statement, me, super,
                                                  classes, templates, exception,
                                                  stack, parameters, fields,
                                                  get_input, output, error,
                                                  trace_output)
                if latest_order[0]:
                    return latest_order
        case [InterpreterBase.THROW_DEF, exception_expression]:
            try:
                raise Complaint(evaluate_expression(exception_expression, me,
                                                    super, classes, templates,
                                                    exception, stack,
                                                    parameters, fields, error,
                                                    trace_output))
            except ValueError as e:
                error(ErrorType.TYPE_ERROR, str(e), statement[0].line_num)
        case [InterpreterBase.TRY_DEF, try_statement, catch_statement]:
            try:
                order = evaluate_statement(try_statement, me, super, classes,
                                           templates, exception, stack,
                                           parameters, fields, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
            except Complaint as e:
                order = evaluate_statement(catch_statement, me, super, classes,
                                           templates, e.message, stack,
                                           parameters, fields, get_input,
                                           output, error, trace_output)
                if order[0]:
                    return order
        case _:
            error(ErrorType.SYNTAX_ERROR, f"Not a valid statement: {statement}")
    return False, None


Interpreter = Barista


def main():
    interpreter = Interpreter(trace_output=True)
    script = '''
(class main
    (method void foo ()
        (while true
            (begin
                (print "argh")
                #(throw "blah")
                (throw (call me throws))
                (print "yay!")
            )
        )
    )
    (method void throws ()
      (throw "boop")
    )
    (method void bar ()
        (begin
            (print "hello")
            (call me foo)
            (print "bye")
        )
    )
    (method void main ()
        (begin
            (try
                (begin
                    (let ((bool x false) (int y 5))
                        (while (> y 0)
                            (begin
                                (set y (- y 1))
                                (if (== y 0)
                                    #(set x (call me bar))
                                    (while (call me bar)
                                      (print "The exception says: ")
                                    )
                                )
                            )
                        )

                    )
                )

                (begin
                  (let ((int x 5))
                    (while (> x 0)
                      (begin
                        (print exception)
                        (print x)
                        (set x (- x 1))
                      )
                    )
                  )
                )
                 # the catch statement
            )
            (print "woot!")
        )
    )
)
    '''
    try:
        interpreter.run(script.splitlines())
        print(interpreter.get_output())
    except RuntimeError as rare:
        print(rare)
        print(interpreter.get_error_type_and_line())


if __name__ == '__main__':
    main()
