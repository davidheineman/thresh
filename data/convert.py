import csv, json, os, copy, logging, argparse

utils_path = "utils"

def convert_dataset(dataset_name, data_path, output_path, reverse=False):
    logger.info("=" * 60)
    logger.info(f"Dataset name: {dataset_name}")
    logger.info(f"Data path: {data_path}")
    logger.info(f"Output path: {output_path}")
    logger.info(f"Reverse flag: {reverse}")
    logger.info("=" * 60)

    if not os.path.isfile(data_path):
        error_value = f"The provided 'data_path' does not point to an existing file. Recieved: '{data_path}'"
        logger.error(error_value)
        raise ValueError(error_value)

    try:
        dataset_module = __import__(f"utils.{dataset_name}", fromlist=[utils_path])
        logger.info("Converting dataset...")
        if reverse:
            # converted_data = dataset_module.convert_data_backward(data_path, output_path)
            logger.error("Reverse conversion is not yet supported.")
        else:
            converted_data = dataset_module.convert_data_forward(data_path)
            logger.info("Done!")
            
            output_filename = f'{output_path}/{dataset_name}.json'
            logger.info(f"Saving to {output_filename}...")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            with open(output_filename, 'w') as f:
                json.dump(converted_data, f, indent=4)
    except ImportError:
        error_value = f"Dataset '{dataset_name}' is not supported. Supported datasets are {supported_datasets()}"
        logger.error(error_value)
        raise ValueError(error_value)

def supported_datasets():
    return [f[:-3] for f in os.listdir(utils_path) if f.endswith(".py") and f != "__init__.py"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to convert datasets.")
    parser.add_argument("--reverse", action="store_true", help="Use this flag to convert back to the original format.")
    parser.add_argument("--dataset", required=True, help="Name of the dataset, see /utils for names. E.g., 'salsa'")
    parser.add_argument("--data_path", required=True, help="Path to the data. E.g., 'data/salsa_raw.json'")
    parser.add_argument("--output_path", required=True, help="Path to the output. E.g., 'data/salsa'")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    convert_dataset(args.dataset, args.data_path, args.output_path, args.reverse)

    logger.info("Done!")
