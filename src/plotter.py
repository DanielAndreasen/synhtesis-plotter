import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import periodictable as pt
from moogly import MOOG, MOOGSynthOutput

elements1 = {str(e).lower(): e.number for e in pt.elements}
elements2 = {e.name: e.number for e in pt.elements}
elements3 = (e.number for e in pt.elements)
colors = tuple('C{}'.format(i) for i in range(5))


class Plotter:
    def __init__(self, verbose=False, fname=None, linelist=None, atmosphere=None, *args, **kwargs):
        self.verbose = verbose
        self.fname = fname
        self.linelist = linelist
        self.atmosphere = atmosphere
        self.plots = []
        self.number = 26
        self.abundances = '-0.2, 0.0, 0.2'.split(',')
        if self.fname is not None:
            self._read_spectrum()

        self.opt = {'model_in': '\'{}\''.format(self.atmosphere),
                    'lines_in': '\'{}\''.format(self.linelist),
                    'observed_in': '\'{}\''.format(self.fname),
                    'synlimits': '{} {} 0.01 1.00'.format(min(self.wavelength), max(self.wavelength)),
                    'plotpars1': '{} {} 0.00 1.02'.format(min(self.wavelength), max(self.wavelength)),
                    'abundances': '1  {}'.format(len(self.abundances)),
                    'abundances1': '{}  {}'.format(self.number, "  ".join(self.abundances))}

    def _read_spectrum(self):
        d = np.loadtxt(self.fname)
        self.wavelength = d[:, 0]
        self.flux = d[:, 1] / max(d[:, 1])

    def plot(self, *args, **kwargs):
        fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.3)
        self.ax.plot(self.wavelength, self.flux, '-k', lw=4, label='Input')
        plt.xlabel('Wavelength')
        plt.ylabel('Flux')
        self.ax.legend(frameon=False)

        axbox1 = plt.axes([0.2, 0.08, 0.1, 0.075])
        element_box = TextBox(axbox1, ' Element: ', initial='Fe')
        element_box.on_submit(self.update_element)

        axbox2 = plt.axes([0.6, 0.08, 0.25, 0.075])
        abundance_box = TextBox(axbox2, ' Abundances: ', initial='-0.2, 0.0, 0.2')
        abundance_box.on_submit(self.update_abundances)

        plt.show()

    def update_plot(self, mo):
        for plot in self.plots:
            plot.remove()
        self.plots = []
        for abundance, flux, color in zip(self.abundances, mo.flux, colors[0:len(mo.flux)]):
            label = '[{}/H]={}'.format(pt.elements[self.number], abundance)
            l, = self.ax.plot(mo.wavelength, flux, color, label=label)
            self.plots.append(l)
        self.ax.legend(frameon=False)
        plt.draw()

    def update_element(self, text):
        self.number = elements1.get(text.lower(), None) or elements2.get(text.lower(), None)
        if self.number is None:
            if text in map(str, elements3):
                self.number = text
            else:
                raise ValueError('Element %s not found in the periodic table' % text)
                    
        self.opt['abundances1'] = '{}  {}'.format(self.number, "  ".join(self.abundances))
        m = MOOG(verbose=self.verbose, mode='synth', **self.opt)
        mo = m.output
        self.update_plot(mo)

    def update_abundances(self, text):
        self.abundances = text.split(',')
        self.opt['abundances'] = '1  {}'.format(len(self.abundances))
        self.opt['abundances1'] = '{}  {}'.format(self.number, "  ".join(self.abundances))
        m = MOOG(verbose=self.verbose, mode='synth', **self.opt)
        mo = m.output
        self.update_plot(mo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot synthetic spectra')
    parser.add_argument('-i', '--fname', help='Input spectrum (2D text file)')
    parser.add_argument('-l', '--linelist', default='linelist.moog', help='MOOG line list')
    parser.add_argument('-a', '--atmosphere', default='atm.mod', help='Atmosphere model for MOOG')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose')
    args = parser.parse_args()
    p = Plotter(**vars(args))
    p.plot()