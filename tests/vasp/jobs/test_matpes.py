import pytest
from pymatgen.core import Structure

from atomate2.vasp.jobs.base import BaseVaspMaker
from atomate2.vasp.jobs.matpes import MatPESGGAStaticMaker, MatPESMetaGGAStaticMaker

expected_incar = {
    "ALGO": "Normal",
    "EDIFF": 1e-05,
    "ENAUG": 1360,
    "ENCUT": 680,
    "GGA": "PE",
    "ISMEAR": 0,
    "ISPIN": 2,
    "KSPACING": 0.22,
    "LAECHG": True,
    "LASPH": True,
    "LCHARG": True,
    "LMIXTAU": True,
    "LORBIT": 11,
    "LREAL": False,
    "LWAVE": False,
    "NELM": 200,
    "NSW": 0,
    "PREC": "Accurate",
    "SIGMA": 0.05,
    "LDAU": False,
    "LDAUJ": {
        "F": {"Co": 0, "Cr": 0, "Fe": 0, "Mn": 0, "Mo": 0, "Ni": 0, "V": 0, "W": 0},
        "O": {"Co": 0, "Cr": 0, "Fe": 0, "Mn": 0, "Mo": 0, "Ni": 0, "V": 0, "W": 0},
    },
    "LDAUL": {
        "F": {"Co": 2, "Cr": 2, "Fe": 2, "Mn": 2, "Mo": 2, "Ni": 2, "V": 2, "W": 2},
        "O": {"Co": 2, "Cr": 2, "Fe": 2, "Mn": 2, "Mo": 2, "Ni": 2, "V": 2, "W": 2},
    },
    "LDAUTYPE": 2,
    "LDAUU": {
        "F": {
            "Co": 3.32,
            "Cr": 3.7,
            "Fe": 5.3,
            "Mn": 3.9,
            "Mo": 4.38,
            "Ni": 6.2,
            "V": 3.25,
            "W": 6.2,
        },
        "O": {
            "Co": 3.32,
            "Cr": 3.7,
            "Fe": 5.3,
            "Mn": 3.9,
            "Mo": 4.38,
            "Ni": 6.2,
            "V": 3.25,
            "W": 6.2,
        },
    },
}


@pytest.mark.parametrize("maker_cls", [MatPESGGAStaticMaker, MatPESMetaGGAStaticMaker])
def test_matpes_gga_static_maker_default_values(maker_cls: BaseVaspMaker):
    maker = maker_cls()
    assert (
        maker.name
        == f"MatPES {'meta-' if 'Meta' in maker_cls.__name__ else ''}GGA static"
    )
    config = maker.input_set_generator.config_dict
    assert {*config} == {"INCAR", "POTCAR", "PARENT", "POTCAR_FUNCTIONAL"}
    assert config["INCAR"] == expected_incar


def test_matpes_gga_static_maker(mock_vasp, clean_dir, vasp_test_dir):
    from emmet.core.tasks import TaskDoc
    from jobflow import run_locally

    # map from job name to directory containing reference output files
    ref_paths = {
        # TODO should be using GGA-specific reference files here but since they only
        # differ in "GGA", "METAGGA", "ALGO" settings, we avoid a lot of mostly
        # duplicate test files by not checking for these settings
        "MatPES GGA static": "matpes_metagga_static",
    }
    si_struct = Structure.from_file(
        f"{vasp_test_dir}/matpes_metagga_static/inputs/POSCAR"
    )

    # settings passed to fake_run_vasp; adjust these to check for certain INCAR settings
    fake_run_vasp_kwargs = {key: {"incar_settings": []} for key in ref_paths}

    mock_vasp(ref_paths, fake_run_vasp_kwargs)

    # generate flow
    job = MatPESGGAStaticMaker().make(si_struct)

    # ensure flow runs successfully
    responses = run_locally(job, create_folders=True, ensure_success=True)

    # validate output
    output = responses[job.uuid][1].output
    assert isinstance(output, TaskDoc)
    assert output.output.energy == pytest.approx(-238.02634906)


def test_matpes_meta_gga_static_maker(mock_vasp, clean_dir, vasp_test_dir):
    from emmet.core.tasks import TaskDoc
    from jobflow import run_locally

    # map from job name to directory containing reference output files
    ref_paths = {
        "MatPES meta-GGA static": "matpes_metagga_static",
    }
    si_struct = Structure.from_file(
        f"{vasp_test_dir}/matpes_metagga_static/inputs/POSCAR"
    )

    # settings passed to fake_run_vasp; adjust these to check for certain INCAR settings
    fake_run_vasp_kwargs = {
        key: {"incar_settings": ["GGA", "METAGGA", "ALGO"]} for key in ref_paths
    }

    mock_vasp(ref_paths, fake_run_vasp_kwargs)

    # generate flow
    job = MatPESMetaGGAStaticMaker().make(si_struct)

    # ensure flow runs successfully
    responses = run_locally(job, create_folders=True, ensure_success=True)

    # validate output
    output = responses[job.uuid][1].output
    assert isinstance(output, TaskDoc)
    assert output.output.energy == pytest.approx(-238.02634906)
