"""
Test postprocessing utilities
"""

import numpy as np
import flopy
from flopy.utils.postprocessing import (
    get_transmissivities,
    get_water_table,
    get_gradients,
)

mf = flopy.modflow


def test_get_transmissivities():
    sctop = [-0.25, 0.5, 1.7, 1.5, 3.0, 2.5, 3.0, -10.0]
    scbot = [-1.0, -0.5, 1.2, 0.5, 1.5, -0.2, 2.5, -11.0]
    heads = np.array(
        [
            [1.0, 2.0, 2.05, 3.0, 4.0, 2.5, 2.5, 2.5],
            [1.1, 2.1, 2.2, 2.0, 3.5, 3.0, 3.0, 3.0],
            [1.2, 2.3, 2.4, 0.6, 3.4, 3.2, 3.2, 3.2],
        ]
    )
    nl, nr = heads.shape
    nc = nr
    botm = np.ones((nl, nr, nc), dtype=float)
    top = np.ones((nr, nc), dtype=float) * 2.1
    hk = np.ones((nl, nr, nc), dtype=float) * 2.0
    for i in range(nl):
        botm[nl - i - 1, :, :] = i

    m = mf.Modflow("junk", version="mfnwt", model_ws="temp")
    dis = mf.ModflowDis(m, nlay=nl, nrow=nr, ncol=nc, botm=botm, top=top)
    upw = mf.ModflowUpw(m, hk=hk)

    # test with open intervals
    r, c = np.arange(nr), np.arange(nc)
    T = get_transmissivities(heads, m, r=r, c=c, sctop=sctop, scbot=scbot)
    assert (
        T
        - np.array(
            [
                [0.0, 0, 0.0, 0.0, 0.2, 0.2, 2.0, 0.0],
                [0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 0.0, 0.0],
                [2.0, 1.0, 0.0, 0.2, 0.0, 2.0, 0.0, 2.0],
            ]
        )
    ).sum() < 1e-3

    # test without specifying open intervals
    T = get_transmissivities(heads, m, r=r, c=c)
    assert (
        T
        - np.array(
            [
                [0.0, 0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.2],
                [0.2, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
                [2.0, 2.0, 2.0, 1.2, 2.0, 2.0, 2.0, 2.0],
            ]
        )
    ).sum() < 1e-3


def test_get_water_table():
    nodata = -9999.0
    hds = np.ones((3, 3, 3), dtype=float) * nodata
    hds[-1, :, :] = 2.0
    hds[1, 1, 1] = 1.0
    wt = get_water_table(hds, nodata=nodata)
    assert wt.shape == (3, 3)
    assert wt[1, 1] == 1.0
    assert np.sum(wt) == 17.0

    hds2 = np.array([hds, hds])
    wt = get_water_table(hds2, nodata=nodata)
    assert wt.shape == (2, 3, 3)
    assert np.sum(wt[:, 1, 1]) == 2.0
    assert np.sum(wt) == 34.0

    wt = get_water_table(hds2, nodata=nodata, per_idx=0)
    assert wt.shape == (3, 3)
    assert wt[1, 1] == 1.0
    assert np.sum(wt) == 17.0


def test_get_sat_thickness_gradients():
    nodata = -9999.0
    hds = np.ones((3, 3, 3), dtype=float) * nodata
    hds[1, :, :] = 2.4
    hds[0, 1, 1] = 3.2
    hds[2, :, :] = 2.5
    hds[1, 1, 1] = 3.0
    hds[2, 1, 1] = 2.6

    nl, nr, nc = hds.shape
    botm = np.ones((nl, nr, nc), dtype=float)
    top = np.ones((nr, nc), dtype=float) * 4.0
    botm[0, :, :] = 3.0
    botm[1, :, :] = 2.0

    m = mf.Modflow("junk", version="mfnwt", model_ws="temp")
    dis = mf.ModflowDis(m, nlay=nl, nrow=nr, ncol=nc, botm=botm, top=top)
    lpf = mf.ModflowLpf(m, laytyp=np.ones(nl))

    grad = get_gradients(hds, m, nodata=nodata)
    dh = np.diff(hds[:, 1, 1])
    dz = np.array([-0.7, -1.0])
    assert np.abs(dh / dz - grad[:, 1, 1]).sum() < 1e-6
    dh = np.diff(hds[:, 1, 0])
    dz = np.array([np.nan, -0.9])
    assert np.nansum(np.abs(dh / dz - grad[:, 1, 0])) < 1e-6

    sat_thick = m.modelgrid.saturated_thick(hds, mask=nodata)
    assert (
        np.abs(np.sum(sat_thick[:, 1, 1] - np.array([0.2, 1.0, 1.0]))) < 1e-6
    ), "failed saturated thickness comparison (grid.thick())"


if __name__ == "__main__":
    # test_get_transmissivities()
    # test_get_water_table()
    test_get_sat_thickness_gradients()
