__author__ = "aleaf"

import os

try:
    import matplotlib
except:
    matplotlib = None

import flopy

try:
    import pymake
except:
    pymake = None

from ci_framework import base_test_dir, FlopyTestSetup

base_dir = base_test_dir(__file__, rel_path="temp", verbose=True)

mfexe = "mf2005"
v = flopy.which(mfexe)
run = True
if v is None:
    run = False

print(os.getcwd())

if os.path.split(os.getcwd())[-1] == "flopy3":
    path = os.path.join("examples", "data", "mf2005_test")
else:
    path = os.path.join("..", "examples", "data", "mf2005_test")

str_items = {
    0: {
        "mfnam": "str.nam",
        "sfrfile": "str.str",
        "lstfile": "str.lst",
    }
}


def test_str_issue1164():
    model_ws = f"{base_dir}_test_str_issue1164"
    test_setup = FlopyTestSetup(verbose=True, test_dirs=model_ws)

    m = flopy.modflow.Modflow.load(
        str_items[0]["mfnam"],
        exe_name=mfexe,
        model_ws=path,
        verbose=False,
        check=False,
    )

    m.change_model_ws(model_ws)

    # adjust stress period data
    spd0 = m.str.stress_period_data[0]
    spd0["flow"][0] = 2.1149856e6  # 450000000000000000.0000e-17
    m.str.stress_period_data[0] = spd0

    # write model datasets and run fixed
    m.write_input()
    success = m.run_model()
    assert success, "could not run base model"

    # get the budget
    lst_pth = os.path.join(model_ws, str_items[0]["lstfile"])
    base_wb = flopy.utils.MfListBudget(lst_pth).get_dataframes()[0]

    # set the model to free format
    m.set_ifrefm()

    # write model datasets and run revised
    m.write_input()
    success = m.run_model()
    assert success, "could not run revised model"

    # get the revised budget
    revised_wb = flopy.utils.MfListBudget(lst_pth).get_dataframes()[0]

    # test if the budgets are the same
    assert revised_wb.equals(base_wb), "water budgets do not match"


def test_str_fixed_free():
    model_ws = f"{base_dir}_test_str_fixed"
    test_setup = FlopyTestSetup(verbose=True, test_dirs=model_ws)

    m = flopy.modflow.Modflow.load(
        str_items[0]["mfnam"],
        exe_name=mfexe,
        model_ws=path,
        verbose=False,
        check=False,
    )
    m.change_model_ws(model_ws)

    # get pointer to str package
    str = m.str
    str.istcb2 = -1

    # add aux variables to str
    aux_names = ["aux iface", "aux xyz"]
    names = ["iface", "xyz"]
    current, current_seg = flopy.modflow.ModflowStr.get_empty(
        23, 7, aux_names=names
    )

    # copy data from existing stress period data
    for name in str.stress_period_data[0].dtype.names:
        current[:][name] = str.stress_period_data[0][:][name]

    # fill aux variable data
    for idx, c in enumerate(str.stress_period_data[0]):
        for jdx, name in enumerate(names):
            current[idx][name] = idx + jdx * 10

    # replace str data with updated str data
    str = flopy.modflow.ModflowStr(
        m,
        mxacts=str.mxacts,
        nss=str.nss,
        ntrib=str.ntrib,
        ndiv=str.ndiv,
        icalc=str.icalc,
        const=str.const,
        ipakcb=str.ipakcb,
        istcb2=str.istcb2,
        iptflg=str.iptflg,
        irdflg=str.irdflg,
        stress_period_data={0: current},
        segment_data=str.segment_data,
        options=aux_names,
    )

    # add head output to oc file
    oclst = ["PRINT HEAD", "PRINT BUDGET", "SAVE HEAD", "SAVE BUDGET"]
    spd = {(0, 0): oclst, (0, 1): oclst, (0, 2): oclst}
    oc = flopy.modflow.ModflowOc(m, stress_period_data=spd)
    oc.reset_budgetunit()

    # reset ipakcb for str package to get ascii output in lst file
    str.ipakcb = -1

    m.write_input()
    if run:
        try:
            success, buff = m.run_model()
        except:
            success = False
        assert success, "base model run did not terminate successfully"

    # load the fixed format model with aux variables
    try:
        m2 = flopy.modflow.Modflow.load(
            str_items[0]["mfnam"],
            exe_name=mfexe,
            model_ws=model_ws,
            verbose=False,
            check=False,
        )
    except:
        m2 = None

    msg = "could not load the fixed format model with aux variables"
    assert m2 is not None, msg

    model_ws2 = f"{base_dir}_test_str_free"
    test_setup.add_test_dir(model_ws2)

    m.change_model_ws(model_ws2)
    m.set_ifrefm()
    m.write_input()
    if run:
        try:
            success, buff = m.run_model()
        except:
            success = False
        assert success, "free format model run did not terminate successfully"

    # load the free format model
    try:
        m2 = flopy.modflow.Modflow.load(
            str_items[0]["mfnam"],
            exe_name=mfexe,
            model_ws=model_ws2,
            verbose=False,
            check=False,
        )
    except:
        m2 = None

    msg = "could not load the free format model with aux variables"
    assert m2 is not None, msg

    # compare the fixed and free format head files
    if run:
        if pymake is not None:
            fn1 = os.path.join(model_ws, "str.nam")
            fn2 = os.path.join(model_ws2, "str.nam")
            success = pymake.compare_heads(fn1, fn2, verbose=True)
            msg = "fixed and free format input output head files are different"
            assert success, msg


def test_str_plot():
    m = flopy.modflow.Modflow.load(
        str_items[0]["mfnam"], model_ws=path, verbose=True, check=False
    )
    if matplotlib is not None:
        assert isinstance(m.str.plot()[0], matplotlib.axes.Axes)
        matplotlib.pyplot.close()


if __name__ == "__main__":
    test_str_issue1164()
    test_str_fixed_free()
    test_str_plot()
