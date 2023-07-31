from .util import verify_exists
import csv, json, os, copy, logging, importlib

utils_path = "datasets"
folder_based_datasets = ["da-san-martino-etal-2019"]

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
        logger.info("Converting dataset...")
        if reverse:
            # converted_data = dataset_module.convert_data_backward(data_path, output_path)
            logger.error("Reverse conversion is not yet supported.")
        else:
            converted_data = dataset_module.convert_data_forward(data_path, limit=limit)
            logger.info("Done!")
            
            if output_path is None:
                return converted_data

            output_filename = f'{output_path}/{dataset_name}.json'
            logger.info(f"Saving to {output_filename}...")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            with open(output_filename, 'w') as f:
                json.dump(converted_data, f, indent=4)
            return None
    except ImportError:
        error_value = f"Dataset '{dataset_name}' is not supported. {supported_datasets()}"
        logger.error(error_value)
        raise ValueError(error_value)


def supported_datasets():
    if not os.path.exists(utils_path):
        return "Cannot find datasets!"
    return "Supported datasets are " + [f[:-3] for f in os.listdir(utils_path) if f.endswith(".py") and f != "__init__.py"]
