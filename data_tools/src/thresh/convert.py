from .util import verify_exists
import csv, json, os, copy, logging, importlib

utils_path = "datasets"
folder_based_datasets = ["propaganda"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def convert_dataset(dataset_name: str, data_path: str, reverse: bool=False, output_path: str=None, limit: int=None) -> dict:
    """
    Converts to the thresh.tools dataset format from supported dataset formats.
    """
    logger.info("=" * 60)
    logger.info(f"Dataset name: {dataset_name}")
    logger.info(f"Data path: {data_path}")
    logger.info(f"Reverse flag: {reverse}")
    logger.info(f"Output path (Optional): {output_path}")
    logger.info("=" * 60)

    if dataset_name not in folder_based_datasets:
        verify_exists(data_path)
    
    try:
        dataset_module = importlib.import_module(f"thresh.{utils_path}.{dataset_name}")
    except ImportError:
        error_value = f"Dataset '{dataset_name}' is not supported. {supported_datasets()}"
        logger.error(error_value)
        raise ValueError(error_value)

    logger.info("Converting dataset...")
    if reverse:
        if output_path == None:
            raise ValueError('Must specify an output path when saving reverse data.')
        if not os.path.exists(os.path.dirname(output_path)) and os.path.dirname(output_path) != '':
            os.makedirs(os.path.dirname(output_path))
        converted_data = dataset_module.convert_data_backward(data_path, output_path)
        logger.info(f"Done!")
        return
    else:
        converted_data = dataset_module.convert_data_forward(data_path, limit=limit)
        logger.info("Done!")
        
        if output_path is None:
            return converted_data

        logger.info(f"Saving to {output_path}...")
        if not os.path.exists(os.path.dirname(output_path)) and os.path.dirname(output_path) != '':
            os.makedirs(os.path.dirname(output_path))
        with open(output_path, 'w') as f:
            json.dump(converted_data, f, indent=4)
        return converted_data

def supported_datasets():
    if not os.path.exists(utils_path):
        return "Cannot find datasets!"
    return "Supported datasets are " + [f[:-3] for f in os.listdir(utils_path) if f.endswith(".py") and f != "__init__.py"]
