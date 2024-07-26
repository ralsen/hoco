class A:
    y_A = 'Test_A'
    
    def __init__(self):
        self.x = self.B(self)  # Instanz von B, übergibt self (Instanz von A)
    
    def func_A(self):
        print('bin in func_A')
        print(A.B.y_B)
    
    def __str__(self):
        return f'A instance with y_A = {self.y_A}'
    
    def __repr__(self):
        return f"A(y_A='{self.y_A}')"
    
    class B:
        y_B = 'Test_B'
        
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance
        
        def func_B(self):
            print('bin in func_B')
            print(self.outer_instance.y_A)  # Zugriff auf y_A der äußeren Instanz
        
        def __str__(self):
            return f'B instance with y_B = {self.y_B}'
        
        def __repr__(self):
            return f"B(y_B='{self.y_B}')"

z = A()
print(z)
print(z.y_A)        # Gibt 'Test_A' aus
print(z.x)          # Gibt 'B instance with y_B = Test_B' aus
z.func_A()           # Gibt "bin in func_A" und "Test_B" aus
z.x.func_B()         # Gibt "bin in func_B" und "Test_A" aus
print(z.x.y_B)      # Gibt 'Test_B' aus

"""
Erläuterung der Ausgaben:

    print(z.y_A):
        Gibt 'Test_A' aus, da y_A ein Klassenattribut der Klasse A ist.

    print(z.x):
        Gibt die Instanz der Klasse B aus. Die Ausgabe ist ein Objekt-String, 
        der in der Regel die Speicheradresse der Instanz enthält (z.B. <__main__.A.B object at 0x...>). 
        Das ist normal, wenn du eine Instanz direkt druckst.

    z.func_A():
        Zuerst gibt print('bin in func_A') aus, dann print(A.B.y_B), was 'Test_B' ausgibt. 
        Das Attribut y_B gehört zur verschachtelten Klasse B.

    z.x.func_B():
        Zuerst gibt print('bin in func_B') aus, dann print(self.outer_instance.y_A), was 'Test_A' ausgibt. 
        self.outer_instance ist eine Referenz auf die äußere Instanz von A, auf die y_A als Klassenattribut zugegriffen wird.

    print(z.x.y_B):
        Gibt 'Test_B' aus, da y_B ein Klassenattribut der Klasse B ist und z.x eine Instanz von B ist.

Der Code sollte ohne Fehler laufen und die erwarteten Ausgaben generieren. 
Es ist eine übliche Praxis, die Ausgabe von Objekten durch spezielle Methoden wie __str__ oder __repr__ zu formatieren, 
um mehr benutzerfreundliche Informationen zu liefern, aber das ist in deinem Kontext nicht notwendig.  

In Python sind __str__ und __repr__ spezielle Methoden, die für die Darstellung eines Objekts als Zeichenkette verwendet werden. 
Sie ermöglichen es dir, zu definieren, wie Instanzen deiner Klassen als Zeichenketten dargestellt werden, was nützlich ist, 
wenn du Objekte druckst oder in Protokollen speicherst.

    __str__: Wird von str() und print() verwendet und sollte eine benutzerfreundliche Darstellung des Objekts zurückgeben.
    __repr__:   Wird von repr() verwendet und soll eine "offizielle" Zeichenkettendarstellung des Objekts zurückgeben, 
                die idealerweise den Objektzustand vollständig beschreibt und es ermöglicht, eine ähnliche Instanz zu erzeugen. 
                Wenn __str__ nicht definiert ist, wird __repr__ auch von print() verwendet.

Hier ist der überarbeitete Code, der __str__ und __repr__ Methoden enthält:         
"""