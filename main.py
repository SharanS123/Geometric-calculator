p1import math
import re
from collections import defaultdict

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def distance(self, other):
        if isinstance(other, Point):
            return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        else:
            return other.distance_to_point(self)
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def length(self):
        return self.p1.distance(self.p2)
    
    def distance_to_point(self, point):
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        px, py = point.x, point.y
        
        # Vector math for closest point on line
        line_vec = (x2 - x1, y2 - y1)
        point_vec = (px - x1, py - y1)
        line_len = self.length()
        
        if line_len == 0:
            return math.sqrt(point_vec[0]**2 + point_vec[1]**2)
        
        line_unitvec = (line_vec[0]/line_len, line_vec[1]/line_len)
        scalar = point_vec[0]*line_unitvec[0] + point_vec[1]*line_unitvec[1]
        scalar = max(0, min(line_len, scalar))
        
        closest = (x1 + scalar*line_unitvec[0], y1 + scalar*line_unitvec[1])
        return math.sqrt((px - closest[0])**2 + (py - closest[1])**2)
    
    def distance(self, other):
        if isinstance(other, Point):
            return self.distance_to_point(other)
        else:
            return other.distance_to_line(self)
    
    def __repr__(self):
        return f"Line({self.p1}, {self.p2})"

class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = float(radius)
    
    def area(self):
        return math.pi * self.radius**2
    
    def circumference(self):
        return 2 * math.pi * self.radius
    
    def distance_to_point(self, point):
        center_dist = self.center.distance(point)
        return max(0, center_dist - self.radius)
    
    def distance_to_line(self, line):
        line_dist = line.distance_to_point(self.center)
        return max(0, line_dist - self.radius)
    
    def distance(self, other):
        if isinstance(other, Point):
            return self.distance_to_point(other)
        elif isinstance(other, Line):
            return self.distance_to_line(other)
        else:
            return other.distance_to_circle(self)
    
    def __repr__(self):
        return f"Circle({self.center}, {self.radius})"

class Rectangle:
    def __init__(self, p1, p2):
        self.xmin = min(p1.x, p2.x)
        self.ymin = min(p1.y, p2.y)
        self.xmax = max(p1.x, p2.x)
        self.ymax = max(p1.y, p2.y)
    
    def area(self):
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)
    
    def perimeter(self):
        return 2 * ((self.xmax - self.xmin) + (self.ymax - self.ymin))
    
    def distance_to_point(self, point):
        if (self.xmin <= point.x <= self.xmax and 
            self.ymin <= point.y <= self.ymax):
            return 0.0
        
        dx = max(self.xmin - point.x, 0, point.x - self.xmax)
        dy = max(self.ymin - point.y, 0, point.y - self.ymax)
        return math.sqrt(dx**2 + dy**2)
    
    def distance_to_line(self, line):
        # Check if line intersects rectangle
        if (self.xmin <= line.p1.x <= self.xmax and 
            self.ymin <= line.p1.y <= self.ymax) or \
           (self.xmin <= line.p2.x <= self.xmax and 
            self.ymin <= line.p2.y <= self.ymax):
            return 0.0
        
        # Check each edge
        edges = [
            Line(Point(self.xmin, self.ymin), Point(self.xmax, self.ymin)),
            Line(Point(self.xmax, self.ymin), Point(self.xmax, self.ymax)),
            Line(Point(self.xmax, self.ymax), Point(self.xmin, self.ymax)),
            Line(Point(self.xmin, self.ymax), Point(self.xmin, self.ymin))
        ]
        
        return min(edge.distance_to_line(line) for edge in edges)
    
    def distance_to_circle(self, circle):
        # Check if circle center is inside rectangle
        if (self.xmin <= circle.center.x <= self.xmax and 
            self.ymin <= circle.center.y <= self.ymax):
            return 0.0
        
        # Find closest point on rectangle to circle center
        closest_x = max(self.xmin, min(circle.center.x, self.xmax))
        closest_y = max(self.ymin, min(circle.center.y, self.ymax))
        closest_point = Point(closest_x, closest_y)
        
        distance = circle.center.distance(closest_point)
        return max(0, distance - circle.radius)
    
    def distance(self, other):
        if isinstance(other, Point):
            return self.distance_to_point(other)
        elif isinstance(other, Line):
            return self.distance_to_line(other)
        elif isinstance(other, Circle):
            return self.distance_to_circle(other)
        else:
            return other.distance_to_rectangle(self)
    
    def __repr__(self):
        return f"Rectangle(Point({self.xmin}, {self.ymin}), Point({self.xmax}, {self.ymax}))"

class Union:
    def __init__(self, shape1, shape2):
        self.shape1 = shape1
        self.shape2 = shape2
    
    def distance(self, point):
        return min(self.shape1.distance(point), self.shape2.distance(point))
    
    def __repr__(self):
        return f"Union({self.shape1}, {self.shape2})"

class Intersection:
    def __init__(self, shape1, shape2):
        self.shape1 = shape1
        self.shape2 = shape2
    
    def distance(self, point):
        return max(self.shape1.distance(point), self.shape2.distance(point))
    
    def __repr__(self):
        return f"Intersection({self.shape1}, {self.shape2})"

def tokenize(expr):
    tokens = []
    while expr:
        if expr[0].isspace():
            expr = expr[1:]
        elif expr[0] in '(),.=':
            tokens.append(expr[0])
            expr = expr[1:]
        elif expr[0].isalpha() or expr[0] == '_':
            match = re.match(r'[\w_]+', expr)
            tokens.append(match.group())
            expr = expr[match.end():]
        elif expr[0].isdigit() or expr[0] in '+-.':
            match = re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', expr)
            tokens.append(match.group())
            expr = expr[match.end():]
        else:
            raise ValueError(f"Invalid character: '{expr[0]}'")
    return tokens

def parse_primary(tokens, variables):
    if not tokens:
        return None, tokens
    
    token = tokens[0]
    if token == '(':
        tokens = tokens[1:]
        expr, tokens = parse_expression(tokens, variables)
        if tokens and tokens[0] == ')':
            tokens = tokens[1:]
            return expr, tokens
        else:
            raise ValueError("Mismatched parentheses")
    
    if token.replace('.', '', 1).isdigit() or (token.startswith('-') and token[1:].replace('.', '', 1).isdigit()):
        tokens = tokens[1:]
        return float(token), tokens
    
    if token.isidentifier():
        # Constructor call
        if len(tokens) > 1 and tokens[1] == '(':
            func = tokens[0]
            tokens = tokens[2:]  # Skip function name and '('
            args = []
            while tokens and tokens[0] != ')':
                arg, tokens = parse_expression(tokens, variables)
                args.append(arg)
                if tokens and tokens[0] == ',':
                    tokens = tokens[1:]
            if not tokens or tokens[0] != ')':
                raise ValueError("Mismatched parentheses")
            tokens = tokens[1:]  # Skip ')'
            
            if func == 'Point' and len(args) == 2:
                return Point(args[0], args[1]), tokens
            elif func == 'Line' and len(args) == 2:
                return Line(args[0], args[1]), tokens
            elif func == 'Circle' and len(args) == 2:
                return Circle(args[0], args[1]), tokens
            elif func == 'Rectangle' and len(args) == 2:
                return Rectangle(args[0], args[1]), tokens
            elif func == 'Union' and len(args) == 2:
                return Union(args[0], args[1]), tokens
            elif func == 'Intersection' and len(args) == 2:
                return Intersection(args[0], args[1]), tokens
            else:
                raise ValueError(f"Invalid constructor: {func}")
        # Variable
        else:
            if token not in variables:
                raise NameError(f"Undefined variable: {token}")
            expr = variables[token]
            tokens = tokens[1:]
            return expr, tokens
    
    raise ValueError(f"Unexpected token: {token}")

def parse_method_call(expr, tokens, variables):
    while tokens and tokens[0] == '.':
        tokens = tokens[1:]  # Skip '.'
        if not tokens or not tokens[0].isidentifier():
            raise ValueError("Expected method name after '.'")
        method = tokens[0]
        tokens = tokens[1:]  # Skip method name
        
        if not tokens or tokens[0] != '(':
            raise ValueError("Expected '(' after method name")
        tokens = tokens[1:]  # Skip '('
        
        args = []
        while tokens and tokens[0] != ')':
            arg, tokens = parse_expression(tokens, variables)
            args.append(arg)
            if tokens and tokens[0] == ',':
                tokens = tokens[1:]
        
        if not tokens or tokens[0] != ')':
            raise ValueError("Expected ')' after method arguments")
        tokens = tokens[1:]  # Skip ')'
        
        # Call the method
        if not hasattr(expr, method):
            raise AttributeError(f"Object of type {type(expr).__name__} has no method '{method}'")
        method_func = getattr(expr, method)
        expr = method_func(*args)
    
    return expr, tokens

def parse_expression(tokens, variables):
    # Parse primary expression
    expr, tokens = parse_primary(tokens, variables)
    
    # Parse method calls
    expr, tokens = parse_method_call(expr, tokens, variables)
    
    # Parse arithmetic operations
    while tokens and tokens[0] in '+-*/':
        op = tokens[0]
        tokens = tokens[1:]
        right, tokens = parse_primary(tokens, variables)
        right, tokens = parse_method_call(right, tokens, variables)
        
        if op == '+':
            expr = expr + right
        elif op == '-':
            expr = expr - right
        elif op == '*':
            expr = expr * right
        elif op == '/':
            expr = expr / right
    
    return expr, tokens

def main():
    variables = {}
    print("Geometric Calculator. Type 'exit' to quit.")
    
    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue
            if line.lower() == 'exit':
                break
            
            # Handle assignment
            if '=' in line:
                parts = line.split('=', 1)
                var_name = parts[0].strip()
                expr_str = parts[1].strip()
                
                if not var_name.isidentifier():
                    raise ValueError(f"Invalid variable name: {var_name}")
                
                tokens = tokenize(expr_str)
                expr, remaining = parse_expression(tokens, variables)
                if remaining:
                    raise ValueError(f"Unexpected tokens after expression: {' '.join(remaining)}")
                
                variables[var_name] = expr
                print(f"{var_name} = {expr}")
            else:
                tokens = tokenize(line)
                expr, remaining = parse_expression(tokens, variables)
                if remaining:
                    raise ValueError(f"Unexpected tokens after expression: {' '.join(remaining)}")
                print(expr)
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()