import os
from pathlib import Path
from tempfile import tempdir

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_almost_equal

# from ross.materials import steel
# from ross.shaft_element import ShaftElement, ShaftElement6DoF
import ross as rs
from ross.defects.misalignment import MisalignmentFlex
from ross.units import Q_

steel = rs.materials.steel
steel.rho = 7.85e3
steel.E = 2.17e11
#  Rotor with 6 DoFs, with internal damping, with 10 shaft elements, 2 disks and 2 bearings.
i_d = 0
o_d = 0.019
n = 33

# fmt: off
L = np.array(
        [0  ,  25,  64, 104, 124, 143, 175, 207, 239, 271,
        303, 335, 345, 355, 380, 408, 436, 466, 496, 526,
        556, 586, 614, 647, 657, 667, 702, 737, 772, 807,
        842, 862, 881, 914]
        )/ 1000
# fmt: on

L = [L[i] - L[i - 1] for i in range(1, len(L))]

shaft_elem = [
    rs.ShaftElement6DoF(
        material=steel,
        L=l,
        idl=i_d,
        odl=o_d,
        idr=i_d,
        odr=o_d,
        alpha=8.0501,
        beta=1.0e-5,
        rotary_inertia=True,
        shear_effects=True,
    )
    for l in L
]

Id = 0.003844540885417
Ip = 0.007513248437500

disk0 = rs.DiskElement6DoF(n=12, m=2.6375, Id=Id, Ip=Ip)
disk1 = rs.DiskElement6DoF(n=24, m=2.6375, Id=Id, Ip=Ip)

kxx1 = 4.40e5
kyy1 = 4.6114e5
kzz = 0
cxx1 = 27.4
cyy1 = 2.505
czz = 0
kxx2 = 9.50e5
kyy2 = 1.09e8
cxx2 = 50.4
cyy2 = 100.4553

bearing0 = rs.BearingElement6DoF(
    n=4, kxx=kxx1, kyy=kyy1, cxx=cxx1, cyy=cyy1, kzz=kzz, czz=czz
)
bearing1 = rs.BearingElement6DoF(
    n=31, kxx=kxx2, kyy=kyy2, cxx=cxx2, cyy=cyy2, kzz=kzz, czz=czz
)

rotor = rs.Rotor(shaft_elem, [disk0, disk1], [bearing0, bearing1])


@pytest.fixture
def mis_comb():

    massunbt = np.array([5e-4, 0])
    phaseunbt = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),  # Rigidez radial do acoplamento flexivel
        ks=38 * 10 ** (3),  # Rigidez de flexão do acoplamento flexivel
        eCOUPx=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao x
        eCOUPy=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao z
        misalignment_angle=5 * np.pi / 180,  # Angulo do desalinhamento angular (rad)
        TD=0,  # Torque antes do acoplamento
        TL=0,  # Torque dopois do acoplamento
        n1=0,
        speed=1200,
        massunb=massunbt,
        phaseunb=phaseunbt,
        mis_type="combined",
    )

    return misalignment


def test_mis_comb_parameters(mis_comb):
    assert mis_comb.dt == 0.1
    assert mis_comb.tI == 0
    assert mis_comb.tF == 5
    assert mis_comb.kd == 40 * 10 ** (3)
    assert mis_comb.ks == 38 * 10 ** (3)
    assert mis_comb.eCOUPx == 2 * 10 ** (-4)
    assert mis_comb.eCOUPy == 2 * 10 ** (-4)
    assert mis_comb.misalignment_angle == 5 * np.pi / 180
    assert mis_comb.TD == 0
    assert mis_comb.TL == 0
    assert mis_comb.n1 == 0
    assert mis_comb.speed == 1200


def test_mis_comb_forces(mis_comb):
    assert mis_comb.forces[mis_comb.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,-4.40604748,-4.40604748,-4.40604748,-4.40604748,
    -4.40604748,
    ]
    )
        # fmt: on
    )

    assert mis_comb.forces[mis_comb.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,1.0821174,1.0821174,1.0821174,1.0821174,
    1.0821174,
    ]
    )
        # fmt: on
    )

    assert mis_comb.forces[mis_comb.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,4.40604748,4.40604748,4.40604748,4.40604748,
    4.40604748,
    ]
    )
        # fmt: on
    )

    assert mis_comb.forces[mis_comb.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,-1.0821174,-1.0821174,-1.0821174,-1.0821174,
    -1.0821174,
    ]
    )
        # fmt: on
    )


@pytest.fixture
def mis_parallel():

    massunbt = np.array([5e-4, 0])
    phaseunbt = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),  # Rigidez radial do acoplamento flexivel
        ks=38 * 10 ** (3),  # Rigidez de flexão do acoplamento flexivel
        eCOUPx=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao x
        eCOUPy=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao z
        misalignment_angle=5 * np.pi / 180,  # Angulo do desalinhamento angular (rad)
        TD=0,  # Torque antes do acoplamento
        TL=0,  # Torque dopois do acoplamento
        n1=0,
        speed=1200,
        massunb=massunbt,
        phaseunb=phaseunbt,
        mis_type="parallel",
    )

    return misalignment


def test_mis_parallel_parameters(mis_parallel):
    assert mis_parallel.dt == 0.1
    assert mis_parallel.tI == 0
    assert mis_parallel.tF == 5
    assert mis_parallel.kd == 40 * 10 ** (3)
    assert mis_parallel.ks == 38 * 10 ** (3)
    assert mis_parallel.eCOUPx == 2 * 10 ** (-4)
    assert mis_parallel.eCOUPy == 2 * 10 ** (-4)
    assert mis_parallel.misalignment_angle == 5 * np.pi / 180
    assert mis_parallel.TD == 0
    assert mis_parallel.TL == 0
    assert mis_parallel.n1 == 0
    assert mis_parallel.speed == 1200


def test_mis_parallel_forces(mis_parallel):
    assert mis_parallel.forces[mis_parallel.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529, -6.78312529, -6.78312529, -6.78312529, -6.78312529,
    -6.78312529
    ]
    )
        # fmt: on
    )

    assert mis_parallel.forces[mis_parallel.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174, 1.0821174,
    1.0821174, 1.0821174, 1.0821174
    ]
    )
        # fmt: on
    )

    assert mis_parallel.forces[mis_parallel.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529, 6.78312529, 6.78312529, 6.78312529, 6.78312529,
    6.78312529
    ]
    )
        # fmt: on
    )

    assert mis_parallel.forces[mis_parallel.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174, -1.0821174, -1.0821174, -1.0821174, -1.0821174,
    -1.0821174
    ]
    )
        # fmt: on
    )


@pytest.fixture
def mis_angular():

    massunbt = np.array([5e-4, 0])
    phaseunbt = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="flex",
        dt=0.1,
        tI=0,
        tF=5,
        kd=40 * 10 ** (3),  # Rigidez radial do acoplamento flexivel
        ks=38 * 10 ** (3),  # Rigidez de flexão do acoplamento flexivel
        eCOUPx=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao x
        eCOUPy=2 * 10 ** (-4),  # Distancia de desalinhamento entre os eixos - direcao z
        misalignment_angle=5 * np.pi / 180,  # Angulo do desalinhamento angular (rad)
        TD=0,  # Torque antes do acoplamento
        TL=0,  # Torque dopois do acoplamento
        n1=0,
        speed=1200,
        massunb=massunbt,
        phaseunb=phaseunbt,
        mis_type="angular",
    )

    return misalignment


def test_mis_angular_parameters(mis_angular):
    assert mis_angular.dt == 0.1
    assert mis_angular.tI == 0
    assert mis_angular.tF == 5
    assert mis_angular.kd == 40 * 10 ** (3)
    assert mis_angular.ks == 38 * 10 ** (3)
    assert mis_angular.eCOUPx == 2 * 10 ** (-4)
    assert mis_angular.eCOUPy == 2 * 10 ** (-4)
    assert mis_angular.misalignment_angle == 5 * np.pi / 180
    assert mis_angular.TD == 0
    assert mis_angular.TL == 0
    assert mis_angular.n1 == 0
    assert mis_angular.speed == 1200


def test_mis_angular_forces(mis_angular):
    assert mis_angular.forces[mis_angular.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782, 2.37707782, 2.37707782, 2.37707782, 2.37707782,
    2.37707782
    ]
    )
        # fmt: on
    )

    assert mis_angular.forces[mis_angular.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [-2.66453526e-15,  1.66147096e-11,  3.32343042e-11,  4.98774355e-11,
    6.64779343e-11,  8.30784330e-11,  9.97633087e-11,  1.16381571e-10,
    1.32931444e-10,  1.49549262e-10,  1.66149317e-10,  1.82851956e-10,
    1.99536387e-10,  2.16086704e-10,  2.32772024e-10,  2.49321896e-10,
    2.65872213e-10,  2.82556645e-10,  2.99107850e-10,  3.15792725e-10,
    3.32375905e-10,  3.48960416e-10,  3.65779851e-10,  3.82330612e-10,
    3.99150490e-10,  4.15429913e-10,  4.32250680e-10,  4.48800552e-10,
    4.65620431e-10,  4.82170748e-10,  4.98721064e-10,  5.15271381e-10,
    5.31820366e-10,  5.48641577e-10,  5.65191449e-10,  5.81740878e-10,
    5.98291194e-10,  6.15111961e-10,  6.31661390e-10,  6.48481713e-10,
    6.64762023e-10,  6.81716905e-10,  6.97726765e-10,  7.14276194e-10,
    7.31366523e-10,  7.47917284e-10,  7.64467156e-10,  7.81017029e-10,
    7.98106914e-10,  8.14657675e-10,  8.30667091e-10
    ]
    )
        # fmt: on
    )

    assert mis_angular.forces[mis_angular.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [-2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782, -2.37707782, -2.37707782, -2.37707782, -2.37707782,
    -2.37707782
    ]
    )
        # fmt: on
    )

    assert mis_angular.forces[mis_angular.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [ 2.66453526e-15, -1.66147096e-11, -3.32343042e-11, -4.98774355e-11,
    -6.64779343e-11, -8.30784330e-11, -9.97633087e-11, -1.16381571e-10,
    -1.32931444e-10, -1.49549262e-10, -1.66149317e-10, -1.82851956e-10,
    -1.99536387e-10, -2.16086704e-10, -2.32772024e-10, -2.49321896e-10,
    -2.65872213e-10, -2.82556645e-10, -2.99107850e-10, -3.15792725e-10,
    -3.32375905e-10, -3.48960416e-10, -3.65779851e-10, -3.82330612e-10,
    -3.99150490e-10, -4.15429913e-10, -4.32250680e-10, -4.48800552e-10,
    -4.65620431e-10, -4.82170748e-10, -4.98721064e-10, -5.15271381e-10,
    -5.31820366e-10, -5.48641577e-10, -5.65191449e-10, -5.81740878e-10,
    -5.98291194e-10, -6.15111961e-10, -6.31661390e-10, -6.48481713e-10,
    -6.64762023e-10, -6.81716905e-10, -6.97726765e-10, -7.14276194e-10,
    -7.31366523e-10, -7.47917284e-10, -7.64467156e-10, -7.81017029e-10,
    -7.98106914e-10, -8.14657675e-10, -8.30667091e-10
    ]
    )
        # fmt: on
    )


@pytest.fixture
def mis_rigid():

    massunbt = np.array([5e-4, 0])
    phaseunbt = np.array([-np.pi / 2, 0])

    misalignment = rotor.run_misalignment(
        coupling="rigid",
        dt=0.0001,
        tI=0,
        tF=0.005,
        eCOUP=2e-4,
        TD=0,
        TL=0,
        n1=0,
        speed=1200,
        massunb=massunbt,
        phaseunb=phaseunbt,
    )

    return misalignment


def test_mis_rigid_parameters(mis_rigid):
    assert mis_rigid.dt == 0.0001
    assert mis_rigid.tI == 0
    assert mis_rigid.tF == 0.005
    assert mis_rigid.eCOUP == 2e-4
    assert mis_rigid.TD == 0
    assert mis_rigid.TL == 0
    assert mis_rigid.n1 == 0
    assert mis_rigid.speed == 1200


def test_mis_rigid_forces(mis_rigid):
    assert mis_rigid.forces[mis_rigid.n1 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [0.00000000e+00, 4.35077327e+00, 1.74016869e+01, 3.91488533e+01,
    6.95860935e+01, 1.08705071e+02, 1.56495459e+02, 2.12945132e+02,
    2.78040370e+02, 3.51766066e+02, 4.34105922e+02, 5.25042620e+02,
    6.24557977e+02, 7.32633045e+02, 8.49248182e+02, 9.74383073e+02,
    1.10801671e+03, 1.25012733e+03, 1.40069232e+03, 1.55968810e+03,
    1.72708996e+03, 1.90287197e+03, 2.08700679e+03, 2.27946559e+03,
    2.48021792e+03, 2.68923169e+03, 2.90647314e+03, 3.13190686e+03,
    3.36549590e+03, 3.60720183e+03, 3.85698496e+03, 4.11480448e+03,
    4.38061868e+03, 4.65438513e+03, 4.93606092e+03, 5.22560280e+03,
    5.52296736e+03, 5.82811109e+03, 6.14099043e+03, 6.46156176e+03,
    6.78978134e+03, 7.12560511e+03, 7.46898853e+03, 7.81988631e+03,
    8.17825210e+03, 8.54403820e+03, 8.91719521e+03, 9.29767168e+03,
    9.68541388e+03, 1.00803655e+04, 1.04824673e+04
    ]
    )
        # fmt: on
    )

    assert mis_rigid.forces[mis_rigid.n1 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [     0.        ,   -692.44599672,  -1384.75404083,  -2076.79499953,
    -2768.44139806,  -3459.56799182,  -4150.05224107,  -4839.7746707 ,
    -5528.6191021 ,  -6216.47275068,  -6903.22618868,  -7588.77317956,
    -8273.01039621,  -8955.83704056,  -9637.15438648, -10316.86527149,
    -10994.87356432, -11671.08363618, -12345.39986288, -13017.72618248,
    -13687.96572995, -14356.02056573, -15021.79150984, -15685.17808747,
    -16346.07858556, -17004.39021452, -17660.009363  , -18312.83192927,
    -18962.75370847, -19609.67081243, -20253.480097  , -20894.07957191,
    -21531.36876923, -22165.24904892, -22795.62382383, -23422.39869074,
    -24045.4814596 , -24664.78207873, -25280.21245923, -25891.68620789,
    -26499.11828245, -27102.42458774, -27701.52153404, -28296.32558157,
    -28886.75279524, -29472.71843379, -30054.13659524, -30630.91993777,
    -31202.97949103, -31770.22456827, -32332.56278416
    ]
    )
        # fmt: on
    )

    assert mis_rigid.forces[mis_rigid.n2 * 6, :] == pytest.approx(
        # fmt: off
    np.array(
    [ 0.00000000e+00, -4.35077327e+00, -1.74016869e+01, -3.91488533e+01,
    -6.95860935e+01, -1.08705071e+02, -1.56495459e+02, -2.12945132e+02,
    -2.78040370e+02, -3.51766066e+02, -4.34105922e+02, -5.25042620e+02,
    -6.24557977e+02, -7.32633045e+02, -8.49248182e+02, -9.74383073e+02,
    -1.10801671e+03, -1.25012733e+03, -1.40069232e+03, -1.55968810e+03,
    -1.72708996e+03, -1.90287197e+03, -2.08700679e+03, -2.27946559e+03,
    -2.48021792e+03, -2.68923169e+03, -2.90647314e+03, -3.13190686e+03,
    -3.36549590e+03, -3.60720183e+03, -3.85698496e+03, -4.11480448e+03,
    -4.38061868e+03, -4.65438513e+03, -4.93606092e+03, -5.22560280e+03,
    -5.52296736e+03, -5.82811109e+03, -6.14099043e+03, -6.46156176e+03,
    -6.78978134e+03, -7.12560511e+03, -7.46898853e+03, -7.81988631e+03,
    -8.17825210e+03, -8.54403820e+03, -8.91719521e+03, -9.29767168e+03,
    -9.68541388e+03, -1.00803655e+04, -1.04824673e+04
    ]
    )
        # fmt: on
    )

    assert mis_rigid.forces[mis_rigid.n2 * 6 + 1, :] == pytest.approx(
        # fmt: off
    np.array(
    [    0.        ,   692.44599672,  1384.75404083,  2076.79499953,
    2768.44139806,  3459.56799182,  4150.05224107,  4839.7746707 ,
    5528.6191021 ,  6216.47275068,  6903.22618868,  7588.77317956,
    8273.01039621,  8955.83704056,  9637.15438648, 10316.86527149,
    10994.87356432, 11671.08363618, 12345.39986288, 13017.72618248,
    13687.96572995, 14356.02056573, 15021.79150984, 15685.17808747,
    16346.07858556, 17004.39021452, 17660.009363  , 18312.83192927,
    18962.75370847, 19609.67081243, 20253.480097  , 20894.07957191,
    21531.36876923, 22165.24904892, 22795.62382383, 23422.39869074,
    24045.4814596 , 24664.78207873, 25280.21245923, 25891.68620789,
    26499.11828245, 27102.42458774, 27701.52153404, 28296.32558157,
    28886.75279524, 29472.71843379, 30054.13659524, 30630.91993777,
    31202.97949103, 31770.22456827, 32332.56278416
    ]
    )
        # fmt: on
    )
