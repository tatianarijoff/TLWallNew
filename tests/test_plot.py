import os
import unittest
import pytlwall
import pytlwall.plot_util as plot


class TestPlot(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up paths for test files."""
        base_dir = os.path.dirname(__file__)
        cls.input_dir = os.path.join(base_dir, "input")
        cls.cfg_file = os.path.join(cls.input_dir, "one_layer.cfg")
        
    def test_longitudinal_output(self):
        """Testing longitudinal simple plot, scale log"""
        print('\nTesting longitudinal simple plot, scale log')
        read_cfg = pytlwall.CfgIo(self.cfg_file)
        mywall = read_cfg.read_pytlwall()
        mywall.calc_ZLong()
        
        # Output directory
        savedir = os.path.join(os.path.dirname(__file__), 'output', 'one_layer', 'img')
        os.makedirs(savedir, exist_ok=True)
        
        savename = 'ZLong.png'
        imped_type = "L"
        title = 'Longitudinal impedance'
        plot.plot_Z_vs_f_simple(mywall.f, mywall.ZLong, imped_type, title,
                                savedir, savename, xscale='log', yscale='log')

    def test_transverse_output(self):
        """Testing transverse plot, scale log, symlog"""
        print('\nTesting transverse plot, scale log, symlog')
        read_cfg = pytlwall.CfgIo(self.cfg_file)
        mywall = read_cfg.read_pytlwall()
        mywall.calc_ZTrans()
        
        # Output directory
        savedir = os.path.join(os.path.dirname(__file__), 'output', 'one_layer', 'img')
        os.makedirs(savedir, exist_ok=True)
        
        f = mywall.f
        
        # Real part
        savename = 'ZTransReal.png'
        imped_type = "T"
        list_Z = [mywall.ZDipX.real, mywall.ZDipY.real, mywall.ZQuadX.real,
                  mywall.ZQuadY.real]
        title = 'Transverse impedance Real'
        list_label = ['Dipolar X', 'Dipolar Y', 'Quadrupolar X',
                      'Quadrupolar Y']
        plot.plot_list_Z_vs_f(f, list_Z, list_label, 'T', title,
                              savedir, savename, 'log', 'symlog')
        
        # Imaginary part
        savename = 'ZTransImag.png'
        list_Z = [mywall.ZDipX.imag, mywall.ZDipY.imag, mywall.ZQuadX.imag,
                  mywall.ZQuadY.imag]
        list_label = ['Dipolar X', 'Dipolar Y', 'Quadrupolar X',
                      'Quadrupolar Y']
        title = 'Transverse impedance Imaginary Part'
        plot.plot_list_Z_vs_f(f, list_Z, list_label, 'T', title,
                              savedir, savename, 'log', 'symlog')


if __name__ == '__main__':
    unittest.main()
