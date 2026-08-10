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
       code = CodeBuilder()

       code.add_line("def render_function(context, do_dots):")
       code.indent()
       code.add_line('"""Takes `context`, the data dictionary for rendering the template and `do_dots` enables the dot attribute access."""')
       # add variables section
       vars_code = code.add_section()
       code.add_line("result: list = []")
       # define shortcuts for list functions (for performance)
       code.add_line("append_result = result.append")
       code.add_line("extend_result = result.extend")
       code.add_line("to_str = str")


   buffered: list = [] # holds strings that are to be written to our function source code 
   def flush_output(
       self):
       """Force `buffered` output(s) to the code builder."""

       if (len(buffered) == 1):
           # then use append 
           code.add_line("append_result(%s)" % buffered[0])
       elif (len(buffered) > 1):
           # use extend because more than 1
           code.add_line("extend_result([%s])" % ", ".join(buffered))

        del buffered[:] # clear buffer
        

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
                      code.add_line("if %s:" % self._expr_code(words[1]))
                      code.indent()
                  elif (words[0] == "for"):
                      # loop? iterate over expressions
                      if (len(words) != 4 or 
                          words[2] != "in"):
                          self._syntax_error("Unrecognized 'for':", token)
                      # Start `for` code block
                      ops_stack.append("for")
                      self._variable(words[1], self.loop_variables) # _variable checks syntax and adds it to var sets: all_vars, loop_vars
                      code.add_line(
                          "for count_%s in %s:" % (
                              words[1],
                              self._expr_code(words[3])
                          )
                      )
                      code.indent()
                  elif (words[0].startswith("end")):
                      # end an operation - pop ops_stack
                      if (len(words) != 1):
                          self._syntax_error("Unrecognized `end`:", token)

                    















