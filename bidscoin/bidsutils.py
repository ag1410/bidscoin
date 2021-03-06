"""
Module with helper functions
"""

import os
import sys
import logging
import copy
import ruamel
import ntpath
from collections import OrderedDict


logger = logging.getLogger('bidscoin')

MAX_NUM_PROVENANCE_ATTRIBUTES = 2
MAX_NUM_BIDS_ATTRIBUTES = 10
MAX_NUM_BIDS_NAME_ATTRIBUTES = 1


MODALITIES = [
    "anat",
    "func",
    "dwi",
    "fmap",
    "beh",
    "pet",
    "extra_data"
]


BIDS_LABELS = [
    'acq_label',
    'modality_label',
    'ce_label',
    'rec_label',
    'task_label',
    'echo_index',
    'dir_label',
    'suffix'
]


MODALITY_LABELS = [
    'T1w',
    'T2w',
    'T1rho',
    'T1map',
    'T2map',
    'T2star',
    'FLAIR',
    'FLASH',
    'PD',
    'PDmap',
    'PDT2',
    'inplaneT1',
    'inplaneT2',
    'angio',
    'defacemask',
    'SWImagandphase'
]


def show_label(label):
    """Determine if label needs to be shown in BIDS name. """
    if label is None or label == "":
        return False
    else:
        return True


def get_bids_attributes(modality, source_bids_attributes):
    """Return the BIDS attributes (i.e. the key,value pairs). """
    bids_attributes = None

    if modality == 'anat':
        # acq_label: <SeriesDescription>
        # rec_label: ~
        # run_index: <<1>>
        # mod_label: ~
        # modality_label: MODALITY_LABELS
        # ce_label: ~
        bids_attributes = OrderedDict()
        bids_attributes['acq_label'] = source_bids_attributes.get('acq_label', '<SeriesDescription>')
        bids_attributes['rec_label'] = source_bids_attributes.get('rec_label', '')
        bids_attributes['run_index'] = source_bids_attributes.get('run_index', '<<1>>')
        bids_attributes['mod_label'] = source_bids_attributes.get('mod_label', '')
        bids_attributes['modality_label'] = source_bids_attributes.get('modality_label', MODALITY_LABELS[0])
        bids_attributes['ce_label'] = source_bids_attributes.get('ce_label', '')

    elif modality == 'func':
        # task_label: <SeriesDescription>
        # acq_label: ~
        # rec_label: ~
        # run_index: <<1>>
        # echo_index: <EchoNumbers>
        # suffix: bold
        bids_attributes = OrderedDict()
        bids_attributes['task_label'] = source_bids_attributes.get('task_label', '<SeriesDescription>')
        bids_attributes['acq_label'] = source_bids_attributes.get('acq_label', '')
        bids_attributes['rec_label'] = source_bids_attributes.get('rec_label', '')
        bids_attributes['run_index'] = source_bids_attributes.get('run_index', '<<1>>')
        bids_attributes['echo_index'] = source_bids_attributes.get('echo_index', '<EchoNumber>')
        bids_attributes['suffix'] = source_bids_attributes.get('suffix', 'bold')

    elif modality == 'dwi':
        # acq_label: <SeriesDescription>
        # run_index: <<1>>
        # suffix: [dwi, sbref]
        bids_attributes = OrderedDict()
        bids_attributes['acq_label'] = source_bids_attributes.get('acq_label', '<SeriesDescription>')
        bids_attributes['run_index'] = source_bids_attributes.get('run_index', '<<1>>')
        bids_attributes['suffix'] = source_bids_attributes.get('suffix', '')

    elif modality == 'fmap':
        # acq_label: <SeriesDescription>
        # run_index: <<1>>
        # dir_label: None, <InPlanePhaseEncodingDirection>
        # suffix: [magnitude, magnitude1, magnitude2, phasediff, phase1, phase2, fieldmap, epi]
        bids_attributes = OrderedDict()
        bids_attributes['acq_label'] = source_bids_attributes.get('acq_label', '<SeriesDescription>')
        bids_attributes['run_index'] = source_bids_attributes.get('run_index', '<<1>>')
        bids_attributes['dir_label'] = source_bids_attributes.get('dir_label', '')
        bids_attributes['suffix'] = source_bids_attributes.get('suffix', '')

    elif modality == 'beh':
        # task_name: <SeriesDescription>
        # suffix: ~
        bids_attributes = OrderedDict()
        bids_attributes['task_label'] = source_bids_attributes.get('task_label', '<SeriesDescription>')
        bids_attributes['suffix'] = source_bids_attributes.get('suffix', '')

    elif modality == 'pet':
        # task_label: <SeriesDescription>
        # acq_label: <Radiopharmaceutical>
        # rec_label: ~
        # run_index: <<1>>
        # suffix: pet
        bids_attributes = OrderedDict()
        bids_attributes['task_label'] = source_bids_attributes.get('task_label', '<SeriesDescription>')
        bids_attributes['acq_label'] = source_bids_attributes.get('acq_label', '<Radiopharmaceutical>')
        bids_attributes['rec_label'] = source_bids_attributes.get('rec_label', '')
        bids_attributes['run_index'] = source_bids_attributes.get('run_index', '<<1>>')
        bids_attributes['suffix'] = source_bids_attributes.get('suffix', 'pet')

    elif modality == 'extra_data':
        # acq_label: <SeriesDescription>
        # rec_label: ~
        # ce_label: ~
        # task_label: ~
        # echo_index: ~
        # dir_label: ~
        # run_index: <<1>>
        # suffix: ~
        # mod_label: ~
        # modality_label: ~
        bids_attributes = OrderedDict()
        bids_attributes['acq_label'] = source_bids_attributes.get('acq_label', '<SeriesDescription>')
        bids_attributes['rec_label'] = source_bids_attributes.get('rec_label', '')
        bids_attributes['ce_label'] = source_bids_attributes.get('ce_label', '')
        bids_attributes['task_label'] = source_bids_attributes.get('task_label', '')
        bids_attributes['echo_index'] = source_bids_attributes.get('echo_index', '')
        bids_attributes['dir_label'] = source_bids_attributes.get('dir_label', '')
        bids_attributes['suffix'] = source_bids_attributes.get('suffix', '')
        bids_attributes['run_index'] = source_bids_attributes.get('run_index', '<<1>>')
        bids_attributes['mod_label'] = source_bids_attributes.get('mod_label', '')
        bids_attributes['modality_label'] = source_bids_attributes.get('modality_label', '')

    return bids_attributes


def get_bids_name_array(subid, sesid, modality, bids_values, run):
    """Return the components of the BIDS name as an array. """
    acq_label = bids_values.get('acq_label', '')
    ce_label = bids_values.get('ce_label', '')
    rec_label = bids_values.get('rec_label', '')
    task_label = bids_values.get('task_label', '')
    echo_index = bids_values.get('echo_index', '')
    dir_label = bids_values.get('dir_label', '')
    suffix = bids_values.get('suffix', '')

    bids_name_array = []

    if modality == 'anat':
        defacemask = False # TODO: account for defacemask possibility
        suffix = bids_values.get('modality_label', '')
        mod = ''

        # bidsname: sub-<participant_label>[_ses-<session_label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_mod-<label>]_suffix
        bids_name_array = [
            {
                'prefix': 'sub-',
                'label': subid,
                'show': True # mandatory
            },
            {
                'prefix': 'ses-',
                'label': sesid,
                'show': show_label(sesid)
            },
            {
                'prefix': 'acq-',
                'label': acq_label,
                'show': show_label(acq_label)
            },
            {
                'prefix': 'ce-',
                'label': ce_label,
                'show': show_label(ce_label)
            },
            {
                'prefix': 'rec-',
                'label': rec_label,
                'show': show_label(rec_label)
            },
            {
                'prefix': 'run-',
                'label': run,
                'show': show_label(run)
            },
            {
                'prefix': 'mod-',
                'label': mod,
                'show': show_label(mod)
            },
            {
                'prefix': '',
                'label': suffix,
                'show': True # mandatory
            }
        ]

    elif modality == 'func':
        # bidsname: sub-<participant_label>[_ses-<session_label>]_task-<task_label>[_acq-<label>][_rec-<label>][_run-<index>][_echo-<index>]_suffix
        bids_name_array = [
            {
                'prefix': 'sub-',
                'label': subid,
                'show': True # mandatory
            },
            {
                'prefix': 'ses-',
                'label': sesid,
                'show': show_label(sesid)
            },
            {
                'prefix': 'task-',
                'label': task_label,
                'show': True # mandatory
            },
            {
                'prefix': 'acq-',
                'label': acq_label,
                'show': show_label(acq_label)
            },
            {
                'prefix': 'rec-',
                'label': rec_label,
                'show': show_label(rec_label)
            },
            {
                'prefix': 'run-',
                'label': run,
                'show': show_label(run)
            },
            {
                'prefix': 'echo-',
                'label': echo_index,
                'show': show_label(echo_index)
            },
            {
                'prefix': '',
                'label': suffix,
                'show': True # mandatory
            }
        ]

    elif modality == 'dwi':
        # bidsname: sub-<participant_label>[_ses-<session_label>][_acq-<label>][_run-<index>]_suffix
        bids_name_array = [
            {
                'prefix': 'sub-',
                'label': subid,
                'show': True # mandatory
            },
            {
                'prefix': 'ses-',
                'label': sesid,
                'show': show_label(sesid)
            },
            {
                'prefix': 'acq-',
                'label': acq_label,
                'show': show_label(acq_label)
            },
            {
                'prefix': 'run-',
                'label': run,
                'show': show_label(run)
            },
            {
                'prefix': '',
                'label': suffix,
                'show': True # mandatory
            }
        ]

    elif modality == 'fmap':
        # TODO: add more fieldmap logic?
        # bidsname: sub-<participant_label>[_ses-<session_label>][_acq-<label>][_dir-<dir_label>][_run-<run_index>]_suffix
        bids_name_array = [
            {
                'prefix': 'sub-',
                'label': subid,
                'show': True # mandatory
            },
            {
                'prefix': 'ses-',
                'label': sesid,
                'show': show_label(sesid)
            },
            {
                'prefix': 'acq-',
                'label': acq_label,
                'show': show_label(acq_label)
            },
            {
                'prefix': 'dir-',
                'label': dir_label,
                'show': show_label(dir_label)
            },
            {
                'prefix': 'run-',
                'label': run,
                'show': show_label(run)
            },
            {
                'prefix': '',
                'label': suffix,
                'show': True # mandatory
            }
        ]

    elif modality == 'beh':
        # bidsname: sub-<participant_label>[_ses-<session_label>]_task-<task_name>_suffix
        bids_name_array = [
            {
                'prefix': 'sub-',
                'label': subid,
                'show': True # mandatory
            },
            {
                'prefix': 'ses-',
                'label': sesid,
                'show': show_label(sesid)
            },
            {
                'prefix': 'task-',
                'label': task_label,
                'show': True # mandatory
            },
            {
                'prefix': '',
                'label': suffix,
                'show': True # mandatory
            }
        ]

    elif modality == 'pet':
        # bidsname: sub-<participant_label>[_ses-<session_label>]_task-<task_label>[_acq-<label>][_rec-<label>][_run-<index>]_suffix
        bids_name_array = [
            {
                'prefix': 'sub-',
                'label': subid,
                'show': True # mandatory
            },
            {
                'prefix': 'ses-',
                'label': sesid,
                'show': show_label(sesid)
            },
            {
                'prefix': 'task-',
                'label': task_label,
                'show': True # mandatory
            },
            {
                'prefix': 'acq-',
                'label': acq_label,
                'show': show_label(acq_label)
            },
            {
                'prefix': 'rec-',
                'label': rec_label,
                'show': show_label(rec_label)
            },
            {
                'prefix': 'run-',
                'label': run,
                'show': show_label(run)
            },
            {
                'prefix': '',
                'label': suffix,
                'show': True # mandatory
            }
        ]

    elif modality == 'extra_data':
        # bidsname: sub-<participant_label>[_ses-<session_label>]_acq-<label>[..][_suffix]
        bids_name_array = [
            {
                'prefix': 'sub-',
                'label': subid,
                'show': True # mandatory
            },
            {
                'prefix': 'ses-',
                'label': sesid,
                'show': show_label(sesid)
            },
            {
                'prefix': 'acq-',
                'label': acq_label,
                'show': True
            },
            {
                'prefix': 'ce-',
                'label': ce_label,
                'show': show_label(ce_label)
            },
            {
                'prefix': 'rec-',
                'label': rec_label,
                'show': show_label(rec_label)
            },
             {
                'prefix': 'task-',
                'label': task_label,
                'show': show_label(task_label)
            },
            {
                'prefix': 'echo-',
                'label': echo_index,
                'show': show_label(echo_index)
            },
            {
                'prefix': 'dir-',
                'label': dir_label,
                'show': show_label(dir_label)
            },
            {
                'prefix': 'run-',
                'label': run,
                'show': show_label(run)
            },
            {
                'prefix': '',
                'label': suffix,
                'show': show_label(suffix)
            }
        ]

    return bids_name_array


def get_bids_name(bids_name_array):
    array = []
    for i, component in enumerate(bids_name_array):
        if component['show']:
            label = ""
            if component['label'] is not None:
                label = component['label']
            array.append(component['prefix'] + label)
    return '_'.join(array)


def read_yaml_as_string(filename):
    """Obtain the initial BIDSmap as yaml string. """
    if not os.path.exists(filename):
        raise Exception("File not found: {}".format(filename))

    yaml_as_string = ""
    with open(filename) as fp:
        yaml_as_string = fp.read()
    return yaml_as_string


def read_bidsmap(bidsmap_yaml):
    """Read the input BIDSmap YAML string into a dictionary. """
    contents = ruamel.yaml.comments.CommentedMap()
    yaml = ruamel.yaml.YAML()
    try:
        contents = yaml.load(bidsmap_yaml)
    except yaml.YAMLError as exc:
        raise Exception('Error: {}'.format(exc))
    return contents


def save_bidsmap(filename, bidsmap):
    """Save the BIDSmap as a YAML text file. """
    yaml = ruamel.yaml.YAML()
    with open(filename, 'w') as stream:
        yaml.dump(bidsmap, stream)


def get_list_summary(bidsmap):
    """Get the list of files from the BIDS map. """
    list_summary = []

    contents_dicom = bidsmap.get('DICOM', ruamel.yaml.comments.CommentedMap())

    for modality in MODALITIES:

        contents_dicom_modality = contents_dicom.get(modality, None)
        if contents_dicom_modality is not None:
            for item in contents_dicom.get(modality, None):
                if item is not None:

                    provenance = item.get('provenance', None)
                    if provenance is not None:
                        provenance_file = ntpath.basename(provenance)
                        provenance_path = ntpath.dirname(provenance)
                    else:
                        provenance_file = ""
                        provenance_path = ""

                    bids_attributes = item.get('bids', None)
                    if bids_attributes is not None:
                        bids_values = bids_attributes
                    else:
                        bids_values = ruamel.yaml.comments.CommentedMap()

                    subid = '*'
                    sesid = '*'
                    run = bids_values.get('run_index', '*')
                    bids_name_array = get_bids_name_array(subid, sesid, modality, bids_values, run)
                    bids_name = get_bids_name(bids_name_array)

                    list_summary.append({
                        "modality": modality,
                        "provenance_file": provenance_file,
                        "provenance_path": provenance_path,
                        "bids_name": bids_name
                    })

    return list_summary


def get_num_samples(bidsmap, modality):
    """Obtain the number of samples for a give modality. """
    if not modality in MODALITIES:
        raise ValueError("invalid modality '{}'".format(modality))

    bidsmap_dicom = bidsmap.get('DICOM', ruamel.yaml.comments.CommentedMap())
    bidsmap_dicom_modality = bidsmap_dicom.get(modality, None)
    if bidsmap_dicom_modality is not None:
        num_samples = len(bidsmap_dicom_modality)
    else:
        num_samples = 0

    return num_samples


def read_sample(bidsmap, modality, index):
    """Obtain sample from BIDS map. """
    if not modality in MODALITIES:
        raise ValueError("invalid modality '{}'".format(modality))

    num_samples = get_num_samples(bidsmap, modality)
    if index > num_samples:
        raise IndexError("invalid index {} ({} items found)".format(index, num_samples+1))

    bidsmap_sample = ruamel.yaml.comments.CommentedMap()
    bidsmap_dicom = bidsmap.get('DICOM', ruamel.yaml.comments.CommentedMap())
    bidsmap_dicom_modality = bidsmap_dicom.get(modality, None)
    if bidsmap_dicom_modality is not None:
        bidsmap_sample = bidsmap_dicom_modality[index]
    else:
        logger.warning('modality not found {}'.format(modality))

    return bidsmap_sample


def delete_sample(bidsmap, modality, index):
    """Delete a sample from the BIDS map. """
    if not modality in MODALITIES:
        raise ValueError("invalid modality '{}'".format(modality))

    num_samples = get_num_samples(bidsmap, modality)
    if index > num_samples:
        raise IndexError("invalid index {} ({} items found)".format(index, num_samples+1))

    bidsmap_dicom = bidsmap.get('DICOM', ruamel.yaml.comments.CommentedMap())
    bidsmap_dicom_modality = bidsmap_dicom.get(modality, None)
    if bidsmap_dicom_modality is not None:
        del bidsmap['DICOM'][modality][index]
    else:
        logger.warning('modality not found {}'.format(modality))

    return bidsmap


def append_sample(bidsmap, modality, sample):
    """Append a sample to the BIDS map. """
    if not modality in MODALITIES:
        raise ValueError("invalid modality '{}'".format(modality))

    bidsmap_dicom = bidsmap.get('DICOM', ruamel.yaml.comments.CommentedMap())
    bidsmap_dicom_modality = bidsmap_dicom.get(modality, None)
    if bidsmap_dicom_modality is not None:
        bidsmap['DICOM'][modality].append(sample)
    else:
        bidsmap['DICOM'][modality] = [sample]

    return bidsmap


def update_bidsmap(source_bidsmap, source_modality, source_index, target_modality, target_sample):
    """Update the BIDS map:
    1. Remove the source sample from the source modality section
    2. Add the target sample to the target modality section
    """
    if not source_modality in MODALITIES:
        raise ValueError("invalid modality '{}'".format(source_modality))

    if not target_modality in MODALITIES:
        raise ValueError("invalid modality '{}'".format(target_modality))

    target_bidsmap = copy.deepcopy(source_bidsmap)

    # Delete the source sample
    target_bidsmap = delete_sample(target_bidsmap, source_modality, source_index)

    # Append the target sample
    target_bidsmap = append_sample(target_bidsmap, target_modality, target_sample)

    return target_bidsmap
