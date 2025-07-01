"""
CSV Metadata Extraction for CSViper
"""

import os
import csv
import json
import hashlib
import chardet
from typing import Dict, Any, List
from .column_normalizer import ColumnNormalizer
from .exceptions import (
    CSVFileError, CSVParsingError, CSVEncodingError, 
    CSVValidationError, MetadataError, FileSystemError
)


class CSVMetadataExtractor:
    """
    Extracts metadata from CSV files including column information and data analysis.
    """
    
    @staticmethod
    def _validate_column_mapping_uniqueness(metadata: Dict[str, Any]) -> None:
        """
        Validate that all normalized column names in the column_name_mapping are unique.
        
        Args:
            metadata (Dict[str, Any]): Metadata dictionary to validate
            
        Raises:
            ValueError: If duplicate normalized column names are found
        """
        if 'column_name_mapping' not in metadata:
            return
        
        column_mapping = metadata['column_name_mapping']
        normalized_values = list(column_mapping.values())
        
        # Check for duplicates
        seen = set()
        duplicates = set()
        for value in normalized_values:
            if value in seen:
                duplicates.add(value)
            else:
                seen.add(value)
        
        if duplicates:
            # Find which original columns map to the duplicate normalized names
            duplicate_mappings = {}
            for orig_col, norm_col in column_mapping.items():
                if norm_col in duplicates:
                    if norm_col not in duplicate_mappings:
                        duplicate_mappings[norm_col] = []
                    duplicate_mappings[norm_col].append(orig_col)
            
            error_msg = "Duplicate normalized column names found in column_name_mapping:\n"
            for norm_col, orig_cols in duplicate_mappings.items():
                error_msg += f"  '{norm_col}' is mapped from: {orig_cols}\n"
            error_msg += "\nThis would cause SQL column name conflicts. "
            error_msg += "Please manually edit the metadata.json file to ensure all normalized column names are unique."
            
            raise ValueError(error_msg)
    
    @staticmethod
    def fromFileToMetadata(full_path_to_csv_file: str, output_dir: str = None, overwrite_previous: bool = False) -> Dict[str, Any]:
        """
        Extract metadata from a CSV file and optionally save to JSON with hash-based caching.
        
        Args:
            full_path_to_csv_file (str): Absolute path to the local CSV file
            output_dir (str, optional): Directory to save metadata JSON file
            overwrite_previous (bool): Whether to overwrite existing cached metadata
            
        Returns:
            Dict[str, Any]: Metadata dictionary containing file info, columns, and analysis
            
        Raises:
            FileNotFoundError: If the CSV file does not exist
            ValueError: If the CSV file is invalid or has inconsistent structure
        """
        # File validation
        if not os.path.isfile(full_path_to_csv_file):
            raise CSVFileError(f"CSV file not found: {full_path_to_csv_file}", full_path_to_csv_file)
        
        if not os.access(full_path_to_csv_file, os.R_OK):
            raise CSVFileError(f"CSV file is not readable: {full_path_to_csv_file}", full_path_to_csv_file)
        
        print(f"Analyzing CSV file: {os.path.basename(full_path_to_csv_file)}")
        
        # Get basic file info
        filename = os.path.basename(full_path_to_csv_file)
        filename_without_ext = os.path.splitext(filename)[0]
        
        # If output directory is specified, check for cached metadata based on column headers hash
        if output_dir and not overwrite_previous:
            cached_metadata = CSVMetadataExtractor._get_cached_metadata(
                full_path_to_csv_file, output_dir, filename_without_ext
            )
            if cached_metadata:
                return cached_metadata
        
        # Generate new metadata
        file_size = os.path.getsize(full_path_to_csv_file)
        
        # Detect CSV format using csv.Sniffer
        delimiter, quote_char = CSVMetadataExtractor._detect_csv_format(full_path_to_csv_file)
        
        # Extract and normalize column names
        original_columns, normalized_columns = CSVMetadataExtractor._extract_column_names(
            full_path_to_csv_file, delimiter, quote_char
        )
        
        # Create column mapping by position to handle duplicate original names
        column_mapping = {}
        for i, (orig, norm) in enumerate(zip(original_columns, normalized_columns)):
            # Use position-based key for duplicates
            key = f"{orig} (column {i+1})" if original_columns.count(orig) > 1 else orig
            column_mapping[key] = norm
        
        # Analyze column widths
        max_lengths = CSVMetadataExtractor._analyze_column_widths(
            full_path_to_csv_file, delimiter, quote_char, original_columns, normalized_columns
        )
        
        # Generate column headers hash for caching
        column_headers_str = ','.join([col.lower() for col in original_columns])
        column_headers_hash = hashlib.md5(column_headers_str.encode()).hexdigest()
        
        # Get encoding information for metadata
        detected_encoding = CSVMetadataExtractor._get_best_encoding(full_path_to_csv_file)
        
        # Build metadata dictionary
        metadata = {
            "filename": filename,
            "filename_without_extension": filename_without_ext,
            "full_path": full_path_to_csv_file,
            "file_size_bytes": file_size,
            "delimiter": delimiter,
            "quote_character": quote_char,
            "encoding": detected_encoding,
            "encoding_confidence": "high",  # Will be updated with actual confidence if available
            "encoding_notes": "Detected automatically. Can be manually overridden if needed.",
            "original_column_names": original_columns,
            "normalized_column_names": normalized_columns,
            "column_name_mapping": column_mapping,
            "max_column_lengths": max_lengths,
            "total_columns": len(original_columns),
            "column_headers_hash": column_headers_hash
        }
        
        # Save metadata to JSON file if output directory is specified
        if output_dir:
            CSVMetadataExtractor._save_metadata_json(metadata, output_dir, filename_without_ext)
        
        return metadata
    
    @staticmethod
    def _detect_file_encoding(file_path: str) -> str:
        """
        Detect the encoding of a file using chardet by reading a large sample.
        For performance, reads multiple samples from different parts of the file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Detected encoding
            
        Raises:
            CSVEncodingError: If encoding cannot be detected
        """
        try:
            print(f"DEBUG: Reading file samples for encoding detection...")
            
            # Read samples from different parts of the file for better detection
            samples = []
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'rb') as f:
                # Read from beginning (first 100KB)
                samples.append(f.read(100000))
                
                # If file is large enough, read from middle and end
                if file_size > 500000:  # 500KB
                    # Read from middle
                    f.seek(file_size // 2)
                    samples.append(f.read(100000))
                    
                    # Read from near end (but not the very end to avoid incomplete lines)
                    f.seek(max(0, file_size - 200000))
                    samples.append(f.read(100000))
            
            # Combine samples for detection
            combined_sample = b''.join(samples)
            print(f"DEBUG: Analyzing {len(combined_sample):,} bytes for encoding detection...")
                
            result = chardet.detect(combined_sample)
            if result['encoding'] is None:
                raise CSVEncodingError(
                    f"Could not detect file encoding. File may be binary or corrupted.",
                    file_path
                )
            
            confidence = result['confidence']
            encoding = result['encoding']
            
            print(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
            
            # If confidence is low, warn the user
            if confidence < 0.7:
                print(f"Warning: Low confidence in encoding detection ({confidence:.2f}). "
                      f"If you encounter issues, try converting the file to UTF-8.")
            
            return encoding
            
        except Exception as e:
            raise CSVEncodingError(
                f"Error detecting file encoding: {e}",
                file_path
            )
    
    # Class-level cache for encoding detection to avoid re-reading large files
    _encoding_cache = {}
    
    @staticmethod
    def _get_best_encoding(file_path: str) -> str:
        """
        Get the best encoding for reading a file, with fallback strategies.
        Uses caching to avoid re-reading large files multiple times.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Best encoding to use for reading the file
        """
        print(f"DEBUG: _get_best_encoding called for {os.path.basename(file_path)}")
        
        # Check cache first
        if file_path in CSVMetadataExtractor._encoding_cache:
            cached_encoding = CSVMetadataExtractor._encoding_cache[file_path]
            print(f"DEBUG: Using cached encoding: {cached_encoding}")
            return cached_encoding
        
        print(f"DEBUG: No cached encoding found, detecting...")
        
        # First detect the encoding using chardet (reads entire file)
        detected_encoding = CSVMetadataExtractor._detect_file_encoding(file_path)
        print(f"DEBUG: Chardet detected encoding: {detected_encoding}")
        
        # Handle problematic encodings
        if detected_encoding.lower() == 'ascii':
            print(f"DEBUG: ASCII detected, trying fallback encodings...")
            # ASCII detection is often wrong when files contain extended characters
            # Try common encodings that are ASCII-compatible, but only test with a sample
            for fallback_encoding in ['iso-8859-1', 'windows-1252', 'cp1252', 'utf-8']:
                print(f"DEBUG: Testing fallback encoding: {fallback_encoding}")
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        # Read a reasonable sample to verify encoding works
                        f.read(100000)  # Read 100KB sample
                    print(f"ASCII detection was insufficient, using {fallback_encoding} instead")
                    CSVMetadataExtractor._encoding_cache[file_path] = fallback_encoding
                    print(f"DEBUG: Cached encoding {fallback_encoding} for future use")
                    return fallback_encoding
                except UnicodeDecodeError as e:
                    print(f"DEBUG: Fallback encoding {fallback_encoding} failed: {e}")
                    continue
            
            # If all fallbacks fail, use the detected encoding anyway
            print(f"Warning: All encoding fallbacks failed, using detected encoding: {detected_encoding}")
            CSVMetadataExtractor._encoding_cache[file_path] = detected_encoding
            return detected_encoding
        
        print(f"DEBUG: Non-ASCII encoding detected, verifying with sample...")
        # For non-ASCII detected encodings, verify they work with a sample
        try:
            with open(file_path, 'r', encoding=detected_encoding) as f:
                # Read a reasonable sample to verify encoding works
                f.read(100000)  # Read 100KB sample
            print(f"DEBUG: Detected encoding {detected_encoding} verified successfully")
            CSVMetadataExtractor._encoding_cache[file_path] = detected_encoding
            print(f"DEBUG: Cached encoding {detected_encoding} for future use")
            return detected_encoding
        except UnicodeDecodeError:
            # If detected encoding fails, try common fallbacks
            print(f"Detected encoding '{detected_encoding}' failed, trying fallbacks...")
            for fallback_encoding in ['iso-8859-1', 'windows-1252', 'cp1252', 'utf-8']:
                print(f"DEBUG: Testing fallback encoding: {fallback_encoding}")
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        # Read a reasonable sample to verify encoding works
                        f.read(100000)  # Read 100KB sample
                    print(f"Using fallback encoding: {fallback_encoding}")
                    CSVMetadataExtractor._encoding_cache[file_path] = fallback_encoding
                    print(f"DEBUG: Cached encoding {fallback_encoding} for future use")
                    return fallback_encoding
                except UnicodeDecodeError as e:
                    print(f"DEBUG: Fallback encoding {fallback_encoding} failed: {e}")
                    continue
            
            # If all fallbacks fail, return the detected encoding anyway
            print(f"Warning: All fallback encodings failed, using detected encoding: {detected_encoding}")
            CSVMetadataExtractor._encoding_cache[file_path] = detected_encoding
            return detected_encoding
    
    @staticmethod
    def _detect_csv_format(file_path: str) -> tuple:
        """
        Detect CSV delimiter and quote character using csv.Sniffer.
        
        Args:
            file_path (str): Path to CSV file
            
        Returns:
            tuple: (delimiter, quote_char)
            
        Raises:
            CSVParsingError: If CSV format cannot be detected
            CSVEncodingError: If file encoding issues are encountered
        """
        # Get the best encoding for this file
        encoding = CSVMetadataExtractor._get_best_encoding(file_path)
        
        try:
            with open(file_path, 'r', newline='', encoding=encoding) as csvfile:
                # Read a sample of the file for sniffing
                sample = csvfile.read(8192)
                csvfile.seek(0)
                
                # Use csv.Sniffer to detect format
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                
                # Verify the dialect works by trying to read the first few lines
                reader = csv.reader(csvfile, dialect)
                header = next(reader)
                first_row = next(reader, None)
                
                if not header:
                    raise CSVParsingError("CSV file appears to be empty", file_path)
                
                if first_row is None:
                    raise CSVParsingError("CSV file contains only a header row, no data", file_path)
                
                print(f"DEBUG: CSV format detection completed successfully")
                return dialect.delimiter, dialect.quotechar
                
        except UnicodeDecodeError as e:
            raise CSVEncodingError(
                f"Unable to read CSV file with detected encoding '{encoding}': {e}. "
                f"The file may be corrupted or use a different encoding. "
                f"Try converting the file to UTF-8 encoding.",
                file_path,
                encoding
            )
        except csv.Error as e:
            raise CSVParsingError(f"CSV parsing error: {e}", file_path)
        except StopIteration:
            raise CSVParsingError("CSV file does not contain sufficient data", file_path)
        except Exception as e:
            raise CSVParsingError(f"Unexpected error while detecting CSV format: {e}", file_path)
    
    @staticmethod
    def _extract_column_names(file_path: str, delimiter: str, quote_char: str) -> tuple:
        """
        Extract and normalize column names from CSV header.
        
        Args:
            file_path (str): Path to CSV file
            delimiter (str): CSV delimiter
            quote_char (str): CSV quote character
            
        Returns:
            tuple: (original_columns, normalized_column_mapping)
            
        Raises:
            CSVEncodingError: If file encoding issues are encountered
            CSVParsingError: If CSV parsing fails
        """
        # Get the best encoding for this file
        encoding = CSVMetadataExtractor._get_best_encoding(file_path)
        
        try:
            with open(file_path, 'r', newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quote_char)
                original_columns = next(reader)
        except UnicodeDecodeError as e:
            raise CSVEncodingError(
                f"Unable to read CSV header with encoding '{encoding}': {e}",
                file_path
            )
        except Exception as e:
            raise CSVParsingError(f"Error reading CSV header: {e}", file_path)
        
        # Normalize column names
        try:
            normalized_columns = ColumnNormalizer.rename_column_list(original_columns)
        except Exception as e:
            raise MetadataError(f"Error normalizing column names: {e}")
        
        return original_columns, normalized_columns
    
    @staticmethod
    def _analyze_column_widths(file_path: str, delimiter: str, quote_char: str, 
                             original_columns: List[str], normalized_columns: List[str]) -> Dict[str, int]:
        """
        Analyze maximum string length for each column in the CSV file.
        
        Args:
            file_path (str): Path to CSV file
            delimiter (str): CSV delimiter
            quote_char (str): CSV quote character
            original_columns (List[str]): Original column names
            normalized_columns (List[str]): List of normalized column names
            
        Returns:
            Dict[str, int]: Maximum length for each original column name
            
        Raises:
            CSVValidationError: If rows have inconsistent column counts
            CSVEncodingError: If file encoding issues are encountered
        """
        print(f"DEBUG: _analyze_column_widths starting for {len(original_columns)} columns...")
        
        max_lengths = {orig_col: 0 for orig_col in original_columns}
        expected_column_count = len(original_columns)
        
        # Get the best encoding for this file
        encoding = CSVMetadataExtractor._get_best_encoding(file_path)
        print(f"DEBUG: Using encoding {encoding} for column width analysis")
        
        try:
            print(f"DEBUG: Opening file for column width analysis...")
            with open(file_path, 'r', newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quote_char)
                
                print(f"DEBUG: Skipping header row...")
                # Skip header row
                next(reader)
                
                print(f"DEBUG: Starting to process data rows...")
                row_number = 1
                for row in reader:
                    row_number += 1
                    
                    # Print progress every 100,000 rows
                    if row_number % 100000 == 0:
                        print(f"DEBUG: Processed {row_number:,} rows...")
                    
                    # Check column count consistency
                    if len(row) != expected_column_count:
                        raise CSVValidationError(
                            f"Inconsistent column count at row {row_number}: "
                            f"Expected {expected_column_count} columns, found {len(row)}",
                            file_path,
                            row_number
                        )
                    
                    # Update maximum lengths using original column names as keys
                    for i, value in enumerate(row):
                        original_col = original_columns[i]
                        max_lengths[original_col] = max(max_lengths[original_col], len(str(value)))
                
                print(f"DEBUG: Column width analysis completed. Processed {row_number:,} total rows.")
        
        except UnicodeDecodeError as e:
            raise CSVEncodingError(
                f"Unable to analyze column widths with encoding '{encoding}': {e}",
                file_path
            )
        except Exception as e:
            raise CSVValidationError(f"Error analyzing column widths: {e}", file_path)
        
        return max_lengths
    
    @staticmethod
    def _get_cached_metadata(csv_file_path: str, output_dir: str, filename_base: str) -> Dict[str, Any]:
        """
        Check for cached metadata based on column headers hash.
        
        Args:
            csv_file_path (str): Path to the CSV file
            output_dir (str): Output directory where metadata might be cached
            filename_base (str): Base filename (without extension)
            
        Returns:
            Dict[str, Any]: Cached metadata if found and headers match, None otherwise
        """
        # Check if metadata file exists
        json_filename = f"{filename_base}.metadata.json"
        json_path = os.path.join(output_dir, json_filename)
        
        if not os.path.exists(json_path):
            return None
        
        try:
            # Load existing metadata
            with open(json_path, 'r', encoding='utf-8') as jsonfile:
                existing_metadata = json.load(jsonfile)
            
            # Check if the existing metadata has a column headers hash
            if 'column_headers_hash' not in existing_metadata:
                print(f"Existing metadata lacks column headers hash, regenerating...")
                return None
            
            # Get current CSV column headers and generate hash
            delimiter, quote_char = CSVMetadataExtractor._detect_csv_format(csv_file_path)
            original_columns, _ = CSVMetadataExtractor._extract_column_names(
                csv_file_path, delimiter, quote_char
            )
            
            # Generate current column headers hash
            column_headers_str = ','.join([col.lower() for col in original_columns])
            current_hash = hashlib.md5(column_headers_str.encode()).hexdigest()
            
            # Compare hashes
            if existing_metadata['column_headers_hash'] == current_hash:
                print(f"Using cached metadata (column headers unchanged): {json_path}")
                # Update the full path in case the file was moved
                existing_metadata['full_path'] = csv_file_path
                
                # Validate that the cached metadata doesn't have duplicate normalized column names
                CSVMetadataExtractor._validate_column_mapping_uniqueness(existing_metadata)
                
                return existing_metadata
            else:
                print(f"Column headers changed, regenerating metadata...")
                return None
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error reading cached metadata: {e}, regenerating...")
            return None
    
    @staticmethod
    def _save_metadata_json(metadata: Dict[str, Any], output_dir: str, filename_base: str) -> None:
        """
        Save metadata to JSON file.
        
        Args:
            metadata (Dict[str, Any]): Metadata dictionary
            output_dir (str): Output directory
            filename_base (str): Base filename (without extension)
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create JSON filename
        json_filename = f"{filename_base}.metadata.json"
        json_path = os.path.join(output_dir, json_filename)
        
        # Save metadata to JSON file
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(metadata, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Metadata saved to: {json_path}")
