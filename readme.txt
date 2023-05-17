TODO: Rewrite

Although I did not fail any Gradescope tests, I did notice I treat "me"
differently from Barista. (I always evaluate it like an expression, while
Barista treats it differently depending on the context.)

It looks like I also explicitly handle a lot more syntax errors compared to
Barista. Additionally, I treat missing "main"'s as syntax errors, whereas
Barista varies.

Lastly, I catch if a set statement tries to set a variable to the result of
calling a "void method" (which used to be specified in the spec).
