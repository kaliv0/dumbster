class TestClass:
    VAR = 5

    def test_k_1(self):
        assert 1 == 1

    def test_k_2(self):
        x = "abc"
        assert isinstance(x, str)

    def test_k_3(self):
        assert self._static_helper(3, 4) == 8, "7 != 8"

    def test_k_4(self):
        assert self._k_helper(6) == 11, "7 != 8"

    @staticmethod
    def _static_helper(a, b):
        return a + b

    def _k_helper(self, a):
        return a + self.VAR

##############################
def test_1():
    assert 1 == 1

def test_2():
    x = "abc"
    assert isinstance(x, str)

def test_3():
    assert _helper(3, 4)

def test_4():
    assert 2 == 3, "2 != 3"

def _helper(a, b):
    return a + b

def test_5(Foo):
    nt = Foo("Bazz", 345)
    assert nt.name == "Bazz"
    assert nt.age == 345
