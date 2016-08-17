"""
Copyright (c) 2006-2011, NIPY Developers
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
       copyright notice, this list of conditions and the following
       disclaimer in the documentation and/or other materials provided
       with the distribution.

    * Neither the name of the NIPY Developers nor the names of any
       contributors may be used to endorse or promote products derived
       from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Nitime 0.6 code adapted by D. Mingers, Aug 2016
d.mingers@web.de

CONTENT OF THIS FILE:

Tests multitaperes spectral time series analysis.

"""
import os
import unittest
import numpy as np
import numpy.testing as npt
import numpy.testing.decorators as dec
import elephant
from elephant import multitaper_spectral as mts

# Define globally
test_dir_path = os.path.join(elephant.__path__[ 0 ], 'test')


class MultitaperSpectralTests(unittest.TestCase):
    def test_dpss_windows(self):
        "Are the eigenvalues representing spectral concentration near unity"
        # these values from Percival and Walden 1993
        _, l = mts.dpss_windows(31, 6, 4)
        unos = np.ones(4)
        npt.assert_array_almost_equal(l, unos)
        _, l = mts.dpss_windows(31, 7, 4)
        npt.assert_array_almost_equal(l, unos)
        _, l = mts.dpss_windows(31, 8, 4)
        npt.assert_array_almost_equal(l, unos)
        _, l = mts.dpss_windows(31, 8, 4.2)
        npt.assert_array_almost_equal(l, unos)

    def test_dpss_matlab(self):
        """Do the dpss windows resemble the equivalent matlab result
        The variable b is read in from a text file generated by issuing:
        dpss(100,2)
        in matlab
        """
        a, _ = mts.dpss_windows(100, 2, 4)
        b = np.loadtxt(os.path.join(test_dir_path, 'dpss_testdata1.txt'))
        npt.assert_almost_equal(a, b.T)

    def test_get_spectra(self):
        """Testing get_spectra"""
        # TODO: this should be adapted to include the welchs_psd from elephant
        t = np.linspace(0, 16 * np.pi, 2 ** 10)
        x = (np.sin(t) + np.sin(2 * t) + np.sin(3 * t) +
             0.1 * np.random.rand(t.shape[ -1 ]))

        # First test for 1-d data:
        NFFT = 64
        N = x.shape[ -1 ]
        # f_welch = mts.get_spectra(x, method={'this_method': 'welch',
        # 'NFFT': NFFT})
        # f_periodogram = mts.get_spectra(x, method={'this_method':
        # 'periodogram_csd'})
        f_multi_taper = mts.get_spectra(x, method={
            'this_method': 'multi_taper_csd'})

        # npt.assert_equal(f_welch[0].shape, (NFFT // 2 + 1,))
        # npt.assert_equal(f_periodogram[0].shape, (N // 2 + 1,))
        npt.assert_equal(f_multi_taper[ 0 ].shape, (N // 2 + 1,))

        # Test for multi-channel data
        x = np.reshape(x, (2, x.shape[ -1 ] // 2))
        N = x.shape[ -1 ]

        # Make sure you get back the expected shape for different spectra:
        NFFT = 64
        # f_welch = mts.get_spectra(x, method={'this_method': 'welch',
        # 'NFFT': NFFT})
        # f_periodogram = mts.get_spectra(x, method={'this_method': 'periodogram_csd'})
        f_multi_taper = mts.get_spectra(x, method={
            'this_method': 'multi_taper_csd'})

        # npt.assert_equal(f_welch[0].shape[0], NFFT / 2 + 1)
        # npt.assert_equal(f_periodogram[0].shape[0], N / 2 + 1)
        npt.assert_equal(f_multi_taper[ 0 ].shape[ 0 ], N / 2 + 1)

    @dec.slow
    def test_long_dpss_win(self):
        """ Test that very long dpss windows can be generated (using interpolation)"""

        # This one is generated using interpolation:
        a1, e = mts.dpss_windows(166800, 4, 8, interp_from=4096)

        # This one is calculated:
        a2, e = mts.dpss_windows(166800, 4, 8)

        # They should be very similar:
        npt.assert_almost_equal(a1, a2, decimal=5)

        # They should both be very similar to the same one calculated in matlab
        # (using 'a = dpss(166800, 4, 8)').
        test_dir_path = os.path.join(elephant.__path__[ 0 ], 'test')
        matlab_long_dpss = np.load(
            os.path.join(test_dir_path, 'dpss_testdata2.npy'))
        # We only have the first window to compare against:
        # Both for the interpolated case:
        npt.assert_almost_equal(a1[ 0 ], matlab_long_dpss, decimal=5)
        # As well as the calculated case:
        npt.assert_almost_equal(a1[ 0 ], matlab_long_dpss, decimal=5)


def suite():
    suite = unittest.makeSuite(MultitaperSpectralTests, 'test')
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())