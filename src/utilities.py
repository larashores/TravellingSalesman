import numpy as np
import scipy.optimize as opt
import scipy.odr as odr
import inspect


def sci_str(num):
    return '{:e}'.format(num)


def uncertainty_str_decimal(val, dval):
    dstr = sci_str(abs(dval))
    dpow = int(dstr[-3:])
    if sci_str(abs(round(dval, -dpow)))[0] == '1':
        dpow -= 1
    val = round(val, -dpow)
    dval = round(dval, -dpow)

    precision = max(-dpow, 0)
    fmt = '{:.' + str(precision) + 'f}'
    return fmt.format(val), fmt.format(dval)


def uncertainty_str(val, dval):
    """
    Returns a string that holds both a value and an uncertainty

    value: The value
    dvalue: The uncertainty
    """
    vpow = int(sci_str(val)[-3:])
    if -3 <= vpow <= 3:
        return '{} +- {}'.format(*uncertainty_str_decimal(val, dval))
    else:
        val *= 10**-vpow
        dval *= 10**-vpow
        return '({} +- {})e{}'.format(*uncertainty_str_decimal(val, dval), vpow)


def _fit_func(func, xs, ys, dxs=None, dys=None):
    if dxs is None:
        optimal, covarience = opt.curve_fit(func, xs, ys, sigma=dys, absolute_sigma=True)
    else:
        data = odr.RealData(xs, ys, dxs, dys)
        new_func = lambda beta, x: func(x, *beta)
        sig = inspect.signature(func)
        options = len(sig.parameters) - 1
        model = odr.Model(new_func, estimate=lambda data: [1 for _ in range(options)])
        odr_obj = odr.ODR(data, model)
        res = odr_obj.run()
        optimal, covarience = res.beta, res.cov_beta
    stddev = np.sqrt(np.diag(covarience))
    return optimal, stddev


def fit_func(func, xs, ys, dxs=None, dys=None, limits=None):
    if limits:
        trim = lambda values: values[limits[0]:limits[1]] if values is not None else None
        values = [trim(values) for values in (xs, ys, dxs, dys)]
    else:
        values = (xs, ys, dxs, dys)
    return _fit_func(func, *values)


if __name__ == '__main__':
    print(uncertainty_str(321.8, .0324))
    print(uncertainty_str(321.856, .0324))
    print(uncertainty_str(321.856, 3.86))
    print(uncertainty_str(-321.856, 11.34))
    print(uncertainty_str(3.21856e-10, 3.24e-12))
    print(uncertainty_str(3.21856e10, 3.24e8))
    print(uncertainty_str(3.21856e10, 1.24e8))
    print(uncertainty_str(0.02094495456, 9.541774545e-05))
    print(uncertainty_str(0.02094495456, 9.341774545e-05))
    print(uncertainty_str(3559.8838983606497, 21.815841616631992))
