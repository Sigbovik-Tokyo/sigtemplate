"""The Templite class is used to create webpage templates and render them.

The Templite class has two main phases: a compilation and a rendering phase

The templite class accepts text and data as a dictionary of values. Call the compile step once to build the template and then the caller can render it how many ever times as they please. 

The dictionary of values are stored in the Templite object and are available when the template is later rendered. 

"""

class Templite:
    """Templite is the template is the compilation and rendering engine of the Web Template engine"""

   def __init__(
       self, text, *contexts):
       """Constructs a Templite with the given `text`.

       `contexts` are dictionaries of values used for future renderings. They're available after compiling and are good for defining functions or constants we want to be available everywhere.

       Args:
           text: str : Text to be used and rendered in the template
           contexts: tuple : A dictionary of values that can be passed as data to be used for future rendering. 

       Returns:
           An instance of the Templite class.
       """

       self.context: dict = {}
       for context in contexts:
           self.context.update(context)

       
       # Keep track of all variables in the code and the loop variables 
       self.all_variables: set = set()
       self.loop_variables: set = set()

       # Call the code-builder to start our compiled funtion
       self.code = CodeBuilder()

       self.code.add_line("def render_function(context, do_dots):")
       self.code.indent()
       self.code.add_line('"""Takes `context`, the data dictionary for rendering the template and `do_dots` enables the dot attribute access."""')
       # add variables section
       vars_code = self.code.add_section()
       self.code.add_line("result: list = []")
       # define shortcuts for list functions (for performance)
       self.code.add_line("append_result = result.append")
       self.code.add_line("extend_result = result.extend")
       self.code.add_line("to_str = str")

       # now parse the text 
       self.parse_text(text)

       # Unpack all context variables into local ones
       for var_name in self.all_vars - self.loop_vars:
           vars_code.add_line("c_%s = context[%r]" % (var_name, var_name))

       # End of function
       self.code.add_line("return ''.join(result)")
       self.code.dedent()

       # obj to render the template
       self._render_function = self.code.get_globals()['render_function']


   buffered: list = [] # holds strings that are to be written to our function source code 
   def flush_output(
       self):
       """Force `buffered` output(s) to the code builder."""

       if (len(buffered) == 1):
           # then use append 
           self.code.add_line("append_result(%s)" % buffered[0])
       elif (len(buffered) > 1):
           # use extend because more than 1
           self.code.add_line("extend_result([%s])" % ", ".join(buffered))

        del buffered[:] # clear buffer


    def _expr_code(self, expr):
        """Generate a Python expression for `expr`.

        Input:
            Our template expressions can be a single value:
                {{user_name}}
            or can be a complex sequence of attribute accesses and filters:
                {{user.name.localized|upper|escape}}
        
        Args:
            expr: str : a python expression of the form defined above.

        Returns:
            code: str : piece of formatted code after evaluating expressions
        """
        
        # complex expression? pipes?
        if ('|' in expr):
            pipes: list[str] = expr.split('|') # split ever func after each |
            code = self._expr_code(pipes[0])
            
            for function in pipes[1:]:
                self._variable(function, self.all_variables)
                code = "c_%s(%s)" % (func, code)
        elif ('.' in expr):
            # no pipe, so dots instead?
            dots = expr.split(".")
            code = self._expr_code(dots[0])
            args = ', '.join(repr(d) for d in dots[1:])
            code = "do_dots(%s, %s)" % (code, args)
        else:
            self._variable(expr, self.all_variables)
            code = "c_%s" % expr

        return code
        

    ops_stack: list = [] # stack of strings - operate and use as it were a stack
    def parse_tokens(
        self, text):
        """Splits text into tokens and parses each individual token according to their requirements.

        Regex Handling:
            Uses regex to split `text` into tokens. 

            Input: `<p>Topics for {{name}}: {% for t in topics %}{{t}}, {% endfor %}</p>`

            Output: 
            ```
            [
                '<p>Topics for ',               # literal
                '{{name}}',                     # expression
                ': ',                           # literal
                '{% for t in topics %}',        # tag
                '',                             # literal (empty)
                '{{t}}',                        # expression
                ', ',                           # literal
                '{% endfor %}',                 # tag
                '</p>'                          # literal
            ]
            ```

        Args:
            text: str : String text to parse and handle.
        """

        # Split `text` using Regex and return split list
        ## ?s : dot should match \n as well
        ## .*? : match any number of characters - but shortest sequence that matches
        ## {{.*?}} : match an expression, ex: <p> Count: {{count}} <p>
        ## {%.?%} : matches a tag
        ## {#.*?} : matches a comment
        tokens: list[str] = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)

        token: str
        for token in tokens:
            if (token.startswith("{#")):
                # Comment? ignore
                continue
            elif (token.startswith("{{")):
                # Expression? oh no
                ## Remove starting {{ and ending }} and pass
                expression = self._expre_code(token[2:-2].strip())
                buffered.append("to_str(%s)", expression)
            elif (token.startswith("{%)"):
                  # Action tag? Split into words and parse again
                  self.flush_output()

                  ## Again, remove {{ and }}
                  words: list[str] = token[2:-2].strip().split(' ') 

                  ## 3 Possible Cases:
                  ### if - simple error handling
                  ### for - multiple expressions
                  ### end - unindent to define end of if block
                  
                  if (words[0] == "if"):
                      # evaluate the expression in if
                      if (len(words) != 2):
                          # can't have complex expressions
                          self._syntax_error("Unrecognized 'if':", token)

                      # start 'if' block
                      ops_stack.append("if")
                      self.code.add_line("if %s:" % self._expr_code(words[1]))
                      self.code.indent()
                  elif (words[0] == "for"):
                      # loop? iterate over expressions
                      if (len(words) != 4 or 
                          words[2] != "in"):
                          self._syntax_error("Unrecognized 'for':", token)
                      # Start `for` code block
                      ops_stack.append("for")
                      self._variable(words[1], self.loop_variables) # _variable checks syntax and adds it to var sets: all_vars, loop_vars
                      self.code.add_line(
                          "for c_%s in %s:" % (
                              words[1],
                              self._expr_code(words[3])
                          )
                      )
                      self.code.indent()
                  elif (words[0].startswith("end")):
                      # end an operation - pop ops_stack
                      if (len(words) != 1):
                          self._syntax_error("Unrecognized `end`:", token)
                      end_tag: str = words[0][3:]
                      
                      if (not ops_stack or ops_stack == []):
                          self._syntax_error("Too many ends:", token)
                      
                      start_tag: str = ops_stack.pop() # what was the last operation that was begun / started
                      
                      if (start_tag != end_tag):
                          self._syntax_error("Mismatched end tag", end_tag, ". Matched with:", start_tag)

                      # de-indent code
                      self.code.dedent()
                  else:
                      # the tag is not: `if`, `for`, `end`
                      self._syntax_error("Unkown tag:", token)
            else:
                # just content
                ## need repr() because it supplies '' around, so it's  
                ## append_result('literal_value')
                ## and not
                ## append_result(literal_value)
                buffered.append(repr(token))

        if (ops_stack or ops_stack != []):
            self._syntax_error("Unmatched action tag:", ops_stack[-1])

        flush_output()


        


                    















