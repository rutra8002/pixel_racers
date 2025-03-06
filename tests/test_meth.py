import math

def test_addition():
    assert 2 + 2 == 4

def test_true():
    assert True != False

def test_sin():
    assert math.sin(0) == 0

def test_cos():
    assert math.cos(0) == 1

def test_sqrt():
    assert math.sqrt(3) == 3**0.5

def test_tan():
    assert math.tan(0) == 0

def test_log():
    assert math.log(1) == 0

def test_log10():
    assert math.log10(1) == 0

def test_log2():
    assert math.log2(1) == 0

def test_log1p():
    assert math.log1p(0) == 0

def test_expm1():
    assert math.expm1(0) == 0

def test_acos():
    assert math.acos(1) == 0

def test_asin():
    assert math.asin(0) == 0

def test_atan():
    assert math.atan(0) == 0