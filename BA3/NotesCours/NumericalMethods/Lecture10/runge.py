import numpy as np
import matplotlib.pyplot as plt
import scipy.linalg as la

def runge(x):
    return 1/(1 + 25*x**2)


def show_all(x, name):
    # x is xs used for sampling
    y = runge(x)
    n = len(x)

    A = np.polynomial.legendre.legvander(x, n-1)
    c = la.solve(A, y)

    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)
    axes.set_ylim([-0.2, 1.2])
    axes.set_xlim([-1.2, 1.2])
    axes.set_axis_off()

    x_th = np.linspace(-1, 1, 1000)
    y_th = np.polynomial.legendre.legvander(x_th, n-1) @ c

    axes.plot(x_th, runge(x_th), '-', color='orange')
    axes.plot(x_th, y_th, '-b')
    axes.plot(x, y, '.r')

    fig.savefig(name, bbox_inches='tight')


n = 20
show_all(np.linspace(-1, 1, n), "rungeProblems.png")
show_all(np.cos((2*np.array(range(n)) + 1)/2/n * np.pi), "rungeChebyshevNodes.png")

