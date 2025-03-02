# Coding Standards

What follows is intended to document as clearly as possible the coding standards used by the Sandman project. As Sandman is comprised of multiple programming languages, there will be a section dedicated to each. However, there may be cases where a particular point may not be clear. If you have questions, please ask on the Sandman Discord.

## Python

Sandman's Python coding standards are based on [PEP 8](https://peps.python.org/pep-0008/). However, there some points that differ. Sandman uses pre-commit to perform linting and formatting using Ruff.

Use f-strings and type hints/annotations whenever possible.

```python
# Right:
f"{some_value} {some_other_value}"
```

```python
# Wrong:
"{} {}".format("Old", "style")
"%s %s" % ("Old", "style")
```

PEP 8 suggests altering spacing around binary operators according to precedence rules. This is discouraged. Instead, explicitly indicate precedence using parentheses and maintain a single space on each side of the operator. Here are some examples:

```python
# Right:
score = multiplier * (points + bonus)
result = (factor1 * value1) + (factor2 * value2)
```

```python
# Wrong:
score = multiplier*(points+bonus)
result = (factor1 *value1)+(factor2* value2)
```

Comparing against True and False is acceptable.


```python
# Okay:
if (skip == True):
   return
```

