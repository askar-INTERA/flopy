# Test vtk export

import numpy as np
import os
import flopy
from flopy.export.vtk import Vtk
from ci_framework import base_test_dir, FlopyTestSetup

base_dir = base_test_dir(__file__, rel_path="temp", verbose=True)


def count_lines_in_file(filepath, binary=False):
    if binary:
        f = open(filepath, "rb")
    else:
        f = open(filepath, "r")
    # note this does not mean much for a binary file but still allows for check
    n = len(f.readlines())
    f.close()
    return n


def test_vtk_export_array2d():
    try:
        import vtk
    except ImportError:
        return

    ws = f"{base_dir}_array_2d_test"
    test_setup = FlopyTestSetup(verbose=True, test_dirs=ws)

    # test mf 2005 freyberg
    mpath = os.path.join(
        "..", "examples", "data", "freyberg_multilayer_transient"
    )
    namfile = "freyberg.nam"
    m = flopy.modflow.Modflow.load(
        namfile, model_ws=mpath, verbose=False, load_only=["dis", "bas6"]
    )

    # export and check
    m.dis.top.export(ws, name="top", fmt="vtk", binary=False)
    filetocheck = os.path.join(ws, "top.vtk")
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 17615

    # with smoothing
    m.dis.top.export(
        ws, fmt="vtk", name="top_smooth", binary=False, smooth=True
    )
    filetocheck = os.path.join(ws, "top_smooth.vtk")
    nlines1 = count_lines_in_file(filetocheck)
    assert nlines1 == 17615


def test_vtk_export_array3d():
    try:
        import vtk
    except ImportError:
        return

    ws = f"{base_dir}_array_3d_test"
    test_setup = FlopyTestSetup(verbose=True, test_dirs=ws)

    # test mf 2005 freyberg
    mpath = os.path.join(
        "..", "examples", "data", "freyberg_multilayer_transient"
    )
    namfile = "freyberg.nam"
    m = flopy.modflow.Modflow.load(
        namfile,
        model_ws=mpath,
        verbose=False,
        load_only=["dis", "bas6", "upw"],
    )

    # export and check
    m.upw.hk.export(ws, fmt="vtk", name="hk", binary=False)
    filetocheck = os.path.join(ws, "hk.vtk")
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 17615

    # with point scalars
    m.upw.hk.export(
        ws,
        fmt="vtk",
        name="hk_points",
        point_scalars=True,
        binary=False,
    )
    filetocheck = os.path.join(ws, "hk_points.vtk")
    nlines1 = count_lines_in_file(filetocheck)
    assert nlines1 == 19482

    # with point scalars and binary
    m.upw.hk.export(
        ws,
        fmt="vtk",
        name="hk_points_bin",
        point_scalars=True,
    )
    filetocheck = os.path.join(ws, "hk_points_bin.vtk")
    assert os.path.exists(filetocheck)


def test_vtk_transient_array_2d():
    try:
        import vtk
    except ImportError:
        return

    test_setup = FlopyTestSetup(verbose=True)

    # test mf 2005 freyberg
    mpath = os.path.join(
        "..", "examples", "data", "freyberg_multilayer_transient"
    )
    namfile = "freyberg.nam"
    m = flopy.modflow.Modflow.load(
        namfile,
        model_ws=mpath,
        verbose=False,
        load_only=["dis", "bas6", "rch"],
    )
    ws = f"{base_dir}_transient_2d_test"
    test_setup.add_test_dir(ws)

    kpers = [0, 1, 1096]

    # export and check
    m.rch.rech.export(ws, fmt="vtk", kpers=kpers, binary=False, xml=True)
    filetocheck = os.path.join(ws, "rech_000001.vtk")
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 26837
    filetocheck = os.path.join(ws, "rech_001096.vtk")
    nlines1 = count_lines_in_file(filetocheck)
    assert nlines1 == 26837

    # with binary
    ws = f"{base_dir}_transient_2d_test_bin"
    test_setup.add_test_dir(ws)

    m.rch.rech.export(ws, fmt="vtk", binary=True, kpers=kpers)
    filetocheck = os.path.join(ws, "rech_000001.vtk")
    assert os.path.exists(filetocheck)
    filetocheck = os.path.join(ws, "rech_001096.vtk")
    assert os.path.exists(filetocheck)


def test_vtk_export_packages():
    try:
        import vtk
    except ImportError:
        return

    test_setup = FlopyTestSetup(verbose=True)

    # test mf 2005 freyberg
    mpath = os.path.join(
        "..", "examples", "data", "freyberg_multilayer_transient"
    )
    namfile = "freyberg.nam"
    m = flopy.modflow.Modflow.load(
        namfile,
        model_ws=mpath,
        verbose=False,
        load_only=["dis", "bas6", "upw", "DRN"],
    )

    # dis export and check
    ws = f"{base_dir}_DIS"
    test_setup.add_test_dir(ws)
    # todo: pakbase.export() for vtk!!!!
    m.dis.export(ws, fmt="vtk", xml=True, binary=False)
    filetocheck = os.path.join(ws, "DIS.vtk")
    # totalbytes = os.path.getsize(filetocheck)
    # assert(totalbytes==1019857)
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 27239, f"nlines ({nlines}) not equal to 27239"

    # upw with point scalar output
    ws = f"{base_dir}_UPW"
    test_setup.add_test_dir(ws)
    m.upw.export(ws, fmt="vtk", xml=True, binary=False, point_scalars=True)
    filetocheck = os.path.join(ws, "UPW.vtk")
    nlines1 = count_lines_in_file(filetocheck)
    assert nlines1 == 42445, f"nlines ({nlines}) not equal to 42445"

    # bas with smoothing on
    ws = f"{base_dir}_BAS_SMOOTH"
    test_setup.add_test_dir(ws)
    m.bas6.export(ws, fmt="vtk", binary=False, smooth=True)
    filetocheck = os.path.join(ws, "BAS6.vtk")
    nlines2 = count_lines_in_file(filetocheck)
    assert nlines2 == 17883

    # transient package drain
    ws = f"{base_dir}_DRN"
    test_setup.add_test_dir(ws)
    kpers = [0, 1, 1096]
    m.drn.export(ws, fmt="vtk", binary=False, xml=True, kpers=kpers, pvd=True)
    filetocheck = os.path.join(ws, "DRN_000001.vtu")
    nlines3 = count_lines_in_file(filetocheck)
    assert nlines3 == 27239
    filetocheck = os.path.join(ws, "DRN_001096.vtu")
    nlines4 = count_lines_in_file(filetocheck)
    assert nlines4 == 27239

    # dis with binary
    ws = f"{base_dir}_DIS_BINARY"
    test_setup.add_test_dir(ws)
    m.dis.export(ws, fmt="vtk", binary=True)
    filetocheck = os.path.join(ws, "DIS.vtk")
    assert os.path.exists(filetocheck)

    # upw with point scalars and binary
    ws = f"{base_dir}_UPW_BINARY"
    test_setup.add_test_dir(ws)
    m.upw.export(ws, fmt="vtk", point_scalars=True, binary=True)
    filetocheck = os.path.join(ws, "UPW.vtk")
    assert os.path.exists(filetocheck)


def test_vtk_mf6():
    try:
        import vtk
    except ImportError:
        return

    test_setup = FlopyTestSetup(verbose=True)

    # test mf6
    mf6expth = os.path.join("..", "examples", "data", "mf6")
    mf6sims = [
        "test045_lake1ss_table",
        "test036_twrihfb",
        "test045_lake2tr",
        "test006_2models_mvr",
    ]

    for simnm in mf6sims:
        print(simnm)
        simpth = os.path.join(mf6expth, simnm)
        loaded_sim = flopy.mf6.MFSimulation.load(simnm, "mf6", "mf6", simpth)
        sim_models = loaded_sim.model_names
        print(sim_models)
        for mname in sim_models:
            print(mname)
            m = loaded_sim.get_model(mname)
            ws = f"{base_dir}_{m.name}"
            test_setup.add_test_dir(ws)
            m.export(ws, fmt="vtk", binary=False)

    # check one
    filetocheck = os.path.join(
        f"{base_dir}_twrihfb2015", "twrihfb2015_000000.vtk"
    )
    # totalbytes = os.path.getsize(filetocheck)
    # assert(totalbytes==21609)
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 9537


def test_vtk_binary_head_export():
    try:
        import vtk
    except ImportError:
        return
    # test mf 2005 freyberg
    from flopy.utils import HeadFile

    test_setup = FlopyTestSetup(verbose=True)

    mpth = os.path.join(
        "..", "examples", "data", "freyberg_multilayer_transient"
    )
    namfile = "freyberg.nam"
    hdsfile = os.path.join(mpth, "freyberg.hds")
    heads = HeadFile(hdsfile)
    m = flopy.modflow.Modflow.load(
        namfile, model_ws=mpth, verbose=False, load_only=["dis", "bas6"]
    )
    filenametocheck = "freyberg_head_000003.vtu"

    # export and check
    ws = f"{base_dir}_heads_test"
    test_setup.add_test_dir(ws)

    vtkobj = Vtk(m, pvd=True, xml=True)
    vtkobj.add_heads(
        heads, kstpkper=[(0, 0), (0, 199), (0, 354), (0, 454), (0, 1089)]
    )
    vtkobj.write(os.path.join(ws, "freyberg_head"))

    filetocheck = os.path.join(ws, filenametocheck)
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 34

    # with point scalars
    ws = f"{base_dir}_heads_test_1"
    test_setup.add_test_dir(ws)

    vtkobj = Vtk(m, pvd=True, xml=True, point_scalars=True)
    vtkobj.add_heads(
        heads, kstpkper=[(0, 0), (0, 199), (0, 354), (0, 454), (0, 1089)]
    )
    vtkobj.write(os.path.join(ws, "freyberg_head"))

    filetocheck = os.path.join(ws, filenametocheck)
    nlines1 = count_lines_in_file(filetocheck)
    assert nlines1 == 34

    # with smoothing
    ws = f"{base_dir}_heads_test_2"
    test_setup.add_test_dir(ws)

    vtkobj = Vtk(m, pvd=True, xml=True, smooth=True)
    vtkobj.add_heads(
        heads, kstpkper=[(0, 0), (0, 199), (0, 354), (0, 454), (0, 1089)]
    )
    vtkobj.write(os.path.join(ws, "freyberg_head"))

    filetocheck = os.path.join(ws, filenametocheck)
    nlines2 = count_lines_in_file(filetocheck)
    assert nlines2 == 34


def test_vtk_cbc():
    try:
        import vtk
    except ImportError:
        return

    test_setup = FlopyTestSetup(verbose=True)

    # test mf 2005 freyberg
    from flopy.utils import CellBudgetFile

    mpth = os.path.join(
        "..", "examples", "data", "freyberg_multilayer_transient"
    )
    namfile = "freyberg.nam"
    cbcfile = os.path.join(mpth, "freyberg.cbc")
    cbc = CellBudgetFile(cbcfile)
    m = flopy.modflow.Modflow.load(
        namfile, model_ws=mpth, verbose=False, load_only=["dis", "bas6"]
    )
    filenametocheck = "freyberg_CBC_000000.vtu"

    # export and check with point scalar
    ws = f"{base_dir}_freyberg_CBC"
    test_setup.add_test_dir(ws)

    vtkobj = Vtk(m, binary=False, xml=True, pvd=True, point_scalars=True)
    vtkobj.add_cell_budget(cbc, kstpkper=[(0, 0), (0, 1), (0, 2)])
    vtkobj.write(os.path.join(ws, "freyberg_CBC"))

    filetocheck = os.path.join(ws, filenametocheck)
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 39243

    # with point scalars and binary
    ws = f"{base_dir}_freyberg_CBC_binary"
    test_setup.add_test_dir(ws)

    vtkobj = Vtk(m, xml=True, pvd=True, point_scalars=True)
    vtkobj.add_cell_budget(cbc, kstpkper=[(0, 0), (0, 1), (0, 2)])
    vtkobj.write(os.path.join(ws, "freyberg_CBC"))
    filetocheck = os.path.join(ws, filenametocheck)
    assert os.path.exists(filetocheck)


def test_vtk_vector():
    try:
        import vtk
    except ImportError:
        return

    from flopy.utils import postprocessing as pp
    from flopy.utils import HeadFile, CellBudgetFile

    test_setup = FlopyTestSetup(verbose=True)

    # test mf 2005 freyberg
    mpth = os.path.join(
        "..", "examples", "data", "freyberg_multilayer_transient"
    )
    namfile = "freyberg.nam"
    cbcfile = os.path.join(mpth, "freyberg.cbc")
    hdsfile = os.path.join(mpth, "freyberg.hds")
    cbc = CellBudgetFile(cbcfile)
    keys = ["FLOW RIGHT FACE", "FLOW FRONT FACE", "FLOW LOWER FACE"]
    vectors = [cbc.get_data(text=t)[0] for t in keys]
    hds = HeadFile(hdsfile)
    head = hds.get_data()
    m = flopy.modflow.Modflow.load(
        namfile, model_ws=mpth, verbose=False, load_only=["dis", "bas6", "upw"]
    )
    q = pp.get_specific_discharge(vectors, m, head)

    filenametocheck = "discharge.vtu"

    # export and check with point scalar
    ws = f"{base_dir}_vector_0"
    test_setup.add_test_dir(ws)

    vtkobj = Vtk(m, xml=True, binary=False, point_scalars=True)
    vtkobj.add_vector(q, "discharge")
    vtkobj.write(os.path.join(ws, filenametocheck))

    filetocheck = os.path.join(ws, filenametocheck)
    nlines = count_lines_in_file(filetocheck)
    assert nlines == 36045

    # with point scalars and binary
    ws = f"{base_dir}_vector_0_binary"
    test_setup.add_test_dir(ws)

    vtkobj = Vtk(m, point_scalars=True)
    vtkobj.add_vector(q, "discharge")
    vtkobj.write(os.path.join(ws, filenametocheck))
    filetocheck = os.path.join(ws, filenametocheck)
    assert os.path.exists(
        filetocheck
    ), f"file (0) does not exist: {filetocheck}"

    # test at cell centers
    q = pp.get_specific_discharge(vectors, m, head)

    ws = f"{base_dir}_vector_1"
    test_setup.add_test_dir(ws)

    filenametocheck = "discharge_verts.vtu"
    vtkobj = Vtk(m, xml=True, binary=False)
    vtkobj.add_vector(q, "discharge")
    vtkobj.write(os.path.join(ws, filenametocheck))

    filetocheck = os.path.join(ws, filenametocheck)
    nlines2 = count_lines_in_file(filetocheck)
    assert nlines2 == 27645, f"nlines != 10598 ({nlines2})"

    ws = f"{base_dir}_vector_1_binary"
    test_setup.add_test_dir(ws)

    # with values directly given at vertices and binary
    vtkobj = Vtk(m, xml=True, binary=False)
    vtkobj.add_vector(q, "discharge")
    vtkobj.write(os.path.join(ws, filenametocheck))

    filetocheck = os.path.join(ws, filenametocheck)
    assert os.path.exists(
        filetocheck
    ), f"file (1) does not exist: {filetocheck}"


def test_vtk_unstructured():
    try:
        import vtk
        from vtk.util import numpy_support
    except ImportError:
        return

    test_setup = FlopyTestSetup(verbose=True)

    def load_verts(fname):
        verts = np.genfromtxt(
            fname, dtype=[int, float, float], names=["iv", "x", "y"]
        )
        verts["iv"] -= 1  # zero based
        return verts

    def load_iverts(fname):
        f = open(fname, "r")
        iverts = []
        xc = []
        yc = []
        for line in f:
            ll = line.strip().split()
            iverts.append([int(i) - 1 for i in ll[4:]])
            xc.append(float(ll[1]))
            yc.append(float(ll[2]))
        return iverts, np.array(xc), np.array(yc)

    u_data_ws = os.path.join("..", "examples", "data", "unstructured")

    # load vertices
    fname = os.path.join(u_data_ws, "ugrid_verts.dat")
    verts = load_verts(fname)

    # load the index list into iverts, xc, and yc
    fname = os.path.join(u_data_ws, "ugrid_iverts.dat")
    iverts, xc, yc = load_iverts(fname)

    # create a 3 layer model grid
    ncpl = np.array(3 * [len(iverts)])
    nnodes = np.sum(ncpl)

    top = np.ones(
        (nnodes),
    )
    botm = np.ones(
        (nnodes),
    )

    # set top and botm elevations
    i0 = 0
    i1 = ncpl[0]
    elevs = [100, 0, -100, -200]
    for ix, cpl in enumerate(ncpl):
        top[i0:i1] *= elevs[ix]
        botm[i0:i1] *= elevs[ix + 1]
        i0 += cpl
        i1 += cpl

    # create the modelgrid
    modelgrid = flopy.discretization.UnstructuredGrid(
        vertices=verts,
        iverts=iverts,
        xcenters=xc,
        ycenters=yc,
        top=top,
        botm=botm,
        ncpl=ncpl,
    )

    ws = f"{base_dir}_unstructured"
    test_setup.add_test_dir(ws)

    outfile = os.path.join(ws, "disu_grid.vtu")
    vtkobj = Vtk(
        modelgrid=modelgrid, vertical_exageration=2, binary=True, smooth=False
    )
    vtkobj.add_array(modelgrid.top, "top")
    vtkobj.add_array(modelgrid.botm, "botm")
    vtkobj.write(outfile)

    if not os.path.exists(outfile):
        raise FileNotFoundError("VTK DISU test file not written")

    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(outfile)
    reader.ReadAllFieldsOn()
    reader.Update()

    data = reader.GetOutput()

    top2 = numpy_support.vtk_to_numpy(data.GetCellData().GetArray("top"))

    if not np.allclose(np.ravel(top), top2):
        raise AssertionError("Field data not properly written")


def test_vtk_vertex():
    try:
        import vtk
        from vtk.util import numpy_support
    except ImportError:
        return

    test_setup = FlopyTestSetup(verbose=True)

    # disv test
    workspace = os.path.join(
        "..", "examples", "data", "mf6", "test003_gwfs_disv"
    )
    # outfile = os.path.join("vtk_transient_test", "vtk_pacakages")
    sim = flopy.mf6.MFSimulation.load(sim_ws=workspace)
    gwf = sim.get_model("gwf_1")

    ws = f"{base_dir}_vertex"
    test_setup.add_test_dir(ws)

    outfile = os.path.join(ws, "disv.vtk")
    vtkobj = Vtk(model=gwf, binary=True, smooth=False)
    vtkobj.add_model(gwf)
    vtkobj.write(outfile)

    outfile = outfile.split(".")[0] + "_000000.vtk"
    if not os.path.exists(outfile):
        raise FileNotFoundError("Vertex VTK File was not written")

    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(outfile)
    reader.ReadAllFieldsOn()
    reader.Update()

    data = reader.GetOutput()

    hk2 = numpy_support.vtk_to_numpy(data.GetCellData().GetArray("k"))
    hk = gwf.npf.k.array
    hk[gwf.modelgrid.idomain == 0] = np.nan

    if not np.allclose(np.ravel(hk), hk2, equal_nan=True):
        raise AssertionError("Field data not properly written")


def test_vtk_pathline():
    try:
        import vtk
        from vtk.util import numpy_support
    except ImportError:
        return

    test_setup = FlopyTestSetup(verbose=True)

    # pathline test for vtk
    ws = os.path.join("..", "examples", "data", "freyberg")
    ml = flopy.modflow.Modflow.load(
        "freyberg.nam", model_ws=ws, exe_name="mf2005"
    )

    ws = f"{base_dir}_pathline"
    test_setup.add_test_dir(ws)

    ml.change_model_ws(new_pth=ws)
    ml.write_input()
    ml.run_model()

    mpp = flopy.modpath.Modpath6(
        "freybergmpp", modflowmodel=ml, model_ws=ws, exe_name="mp6"
    )
    mpbas = flopy.modpath.Modpath6Bas(
        mpp,
        hnoflo=ml.bas6.hnoflo,
        hdry=ml.lpf.hdry,
        ibound=ml.bas6.ibound.array,
        prsity=0.2,
        prsityCB=0.2,
    )
    sim = mpp.create_mpsim(
        trackdir="backward", simtype="pathline", packages="WEL"
    )
    mpp.write_input()
    mpp.run_model()

    pthfile = os.path.join(ws, mpp.sim.pathline_file)
    pthobj = flopy.utils.PathlineFile(pthfile)
    travel_time_max = 200.0 * 365.25 * 24.0 * 60.0 * 60.0
    plines = pthobj.get_alldata(totim=travel_time_max, ge=False)

    outfile = os.path.join(ws, "pathline.vtk")

    vtkobj = Vtk(model=ml, binary=True, vertical_exageration=50, smooth=False)
    vtkobj.add_model(ml)
    vtkobj.add_pathline_points(plines)
    vtkobj.write(outfile)

    outfile = outfile.split(".")[0] + "_pathline.vtk"
    if not os.path.exists(outfile):
        raise FileNotFoundError("Pathline VTK file not properly written")

    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(outfile)
    reader.ReadAllFieldsOn()
    reader.Update()

    data = reader.GetOutput()

    totim = numpy_support.vtk_to_numpy(data.GetCellData().GetArray("time"))
    pid = numpy_support.vtk_to_numpy(data.GetCellData().GetArray("particleid"))

    maxtime = 0
    for p in plines:
        if np.max(p["time"]) > maxtime:
            maxtime = np.max(p["time"])

    if not len(totim) == 12054:
        raise AssertionError("Array size is incorrect for modpath VTK")

    if not np.abs(np.max(totim) - maxtime) < 100:
        raise AssertionError("time values are incorrect for modpath VTK")

    if not len(np.unique(pid)) == len(plines):
        raise AssertionError(
            "number of particles are incorrect for modpath VTK"
        )


if __name__ == "__main__":
    test_vtk_export_array2d()
    test_vtk_export_array3d()
    test_vtk_transient_array_2d()
    test_vtk_export_packages()
    test_vtk_mf6()
    test_vtk_binary_head_export()
    test_vtk_cbc()
    test_vtk_vector()
    test_vtk_unstructured()
    test_vtk_vertex()
    test_vtk_pathline()
