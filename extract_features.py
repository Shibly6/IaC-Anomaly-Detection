#!/usr/bin/env python3
"""
Extract features from Terraform files for anomaly detection.
Fixed version with proper duplicate handling and better feature extraction.
"""

import os
import logging
import pandas as pd
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split

# Import feature extraction modules from existing code
from src.feature_extraction.terraform_parser import parse_terraform_files, create_directories
from src.feature_extraction.feature_engineering import engineer_features_pipeline
from src.feature_extraction.synthetic_data import generate_synthetic_data, augment_with_perturbations
from src.utils.data_preprocessing import preprocess_features, split_dataset

# Configure logging
logger = logging.getLogger("anomaly_detector.extraction")
console = Console()


def extract_features(terraform_dir):
    """
    Extract features from Terraform files with improved processing.
    """
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
    ) as progress:
        # Step 1: Parse Terraform files
        progress_task = progress.add_task("[cyan]Parsing Terraform files...", total=1)
        raw_features = parse_terraform_files(terraform_dir)
        progress.update(progress_task, advance=1)

        # If no features were extracted, generate synthetic data
        if not raw_features:
            logger.warning("No features extracted from Terraform files. Generating synthetic data.")
            raw_features = generate_synthetic_data(sample_count=30)

        # Convert to DataFrame
        features_df = pd.DataFrame(raw_features)
        logger.info(f"Extracted base features for {len(features_df)} configurations")

        # Step 2: Clean and validate data
        progress_task = progress.add_task("[cyan]Cleaning and validating data...", total=1)
        features_df = clean_and_validate_data_fixed(features_df)
        progress.update(progress_task, advance=1)

        # Step 3: Enhanced feature engineering
        progress_task = progress.add_task("[cyan]Engineering discriminative features...", total=1)
        features_df, selected_features, scaler = engineer_features_pipeline_fixed(features_df)
        progress.update(progress_task, advance=1)

        # Step 4: Augment dataset to improve model training
        progress_task = progress.add_task("[cyan]Augmenting dataset...", total=1)
        features_df = augment_dataset_improved(features_df, target_size=100)
        progress.update(progress_task, advance=1)

        logger.info(f"Final dataset shape: {features_df.shape}")

    return features_df, selected_features, scaler


def clean_and_validate_data_fixed(df):
    """
    Clean and validate extracted data with proper handling.
    """
    logger.info("Cleaning and validating extracted data...")

    # Log initial data info
    logger.info(f"Initial dataset: {len(df)} configurations")
    if 'acl' in df.columns:
        acl_counts = df['acl'].value_counts()
        logger.info(f"ACL distribution: {acl_counts.to_dict()}")

    # Only remove exact duplicates based on key features
    duplicate_check_cols = ['bucket_name', 'source_file']
    available_duplicate_cols = [col for col in duplicate_check_cols if col in df.columns]

    if available_duplicate_cols:
        initial_count = len(df)
        df = df.drop_duplicates(subset=available_duplicate_cols, keep='first')
        removed_count = initial_count - len(df)
        logger.info(f"Removed {removed_count} exact duplicates, remaining: {len(df)} configurations")

    # Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            if col.endswith('_enabled') or col in ['is_public_acl', 'has_public_policy']:
                df[col] = df[col].fillna(0)
            elif col.endswith('_score'):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(0)

    # Validate data ranges
    df = validate_data_ranges(df)

    return df


def validate_data_ranges(df):
    """
    Validate and correct data ranges for features.
    """
    # Ensure binary features are 0 or 1
    binary_features = [
        'is_public_acl', 'has_public_policy', 'versioning_enabled', 'logging_enabled',
        'encryption_enabled', 'secure_transport', 'cors_enabled', 'website_enabled',
        'replication_enabled', 'object_lock_enabled', 'intelligent_tiering_enabled',
        'analytics_enabled', 'inventory_enabled', 'accelerate_enabled'
    ]

    for feature in binary_features:
        if feature in df.columns:
            df[feature] = df[feature].clip(0, 1).astype(int)

    # Ensure score features are in reasonable ranges
    score_features = [col for col in df.columns if col.endswith('_score')]
    for feature in score_features:
        if feature in df.columns:
            df[feature] = df[feature].clip(0, 10)

    # Ensure public_access_blocks is 0-4
    if 'public_access_blocks' in df.columns:
        df['public_access_blocks'] = df['public_access_blocks'].clip(0, 4).astype(int)

    return df


def engineer_features_pipeline_fixed(df):
    """
    FIXED: Feature engineering that creates strong discriminative features.
    """
    logger.info("Starting FIXED feature engineering pipeline...")

    try:
        # Step 1: Create STRONG discriminative features
        df = create_strong_discriminative_features(df)
        logger.info(f"After discriminative features: {df.shape[1]} columns")

        # Step 2: Apply the original feature engineering
        df, selected_features, scaler = engineer_features_pipeline(df)

        # Step 3: Ensure we have the most important features
        critical_features = ['main_discriminator', 'public_access_score', 'security_level',
                             'risk_multiplier', 'anomaly_signal']

        for feature in critical_features:
            if feature in df.columns and feature not in selected_features:
                selected_features.insert(0, feature)  # Add at the beginning

        # Limit to reasonable number of features
        selected_features = selected_features[:15]

        return df, selected_features, scaler

    except Exception as e:
        logger.error(f"Error in feature engineering pipeline: {str(e)}")
        # Return basic discriminative features
        basic_features = create_basic_discriminative_features(df)
        return basic_features, ['main_discriminator', 'security_level'], None


def create_strong_discriminative_features(df):
    """
    Create very strong features that clearly separate public vs private buckets.
    """
    df_enhanced = df.copy()

    # MAIN DISCRIMINATOR: Binary feature for public access
    if 'is_public_acl' in df.columns:
        df_enhanced['main_discriminator'] = df_enhanced['is_public_acl'].astype(float)
    else:
        if 'acl' in df.columns:
            df_enhanced['main_discriminator'] = df_enhanced['acl'].apply(
                lambda x: 1.0 if str(x).lower() in ['public-read', 'public-read-write'] else 0.0
            )
        else:
            df_enhanced['main_discriminator'] = 0.0

    # Add policy-based public access
    if 'has_public_policy' in df.columns:
        df_enhanced['main_discriminator'] = np.maximum(
            df_enhanced['main_discriminator'],
            df_enhanced['has_public_policy'].astype(float)
        )

    # SECURITY LEVEL: Graduated security assessment
    security_components = []
    security_features = ['versioning_enabled', 'logging_enabled', 'encryption_enabled', 'secure_transport']

    for feature in security_features:
        if feature in df.columns:
            security_components.append(df_enhanced[feature].fillna(0))

    if security_components:
        df_enhanced['security_level'] = np.sum(security_components, axis=0)
    else:
        df_enhanced['security_level'] = 0

    # RISK MULTIPLIER: Amplify the difference
    df_enhanced['risk_multiplier'] = np.where(
        df_enhanced['main_discriminator'] > 0.5,
        10.0,  # High risk for public buckets
        1.0  # Low risk for private buckets
    )

    # PUBLIC ACCESS SCORE: More nuanced than binary
    if all(col in df_enhanced.columns for col in ['is_public_acl', 'has_public_policy']):
        df_enhanced['public_access_score'] = (
                df_enhanced['is_public_acl'].fillna(0) * 3 +
                df_enhanced['has_public_policy'].fillna(0) * 2
        )

        # Add ACL type weight
        if 'acl' in df_enhanced.columns:
            acl_weights = {
                'private': 0,
                'public-read': 3,
                'public-read-write': 5,
                'authenticated-read': 1
            }
            df_enhanced['public_access_score'] += df_enhanced['acl'].map(
                lambda x: acl_weights.get(str(x).lower(), 0)
            )
    else:
        df_enhanced['public_access_score'] = df_enhanced['main_discriminator'] * 5

    # COMPOSITE ANOMALY SIGNAL
    df_enhanced['anomaly_signal'] = (
            df_enhanced['main_discriminator'] * 10 +
            (4 - df_enhanced['security_level']) * 2 +  # Higher score for less security
            df_enhanced['public_access_score'] * 0.5
    )

    # Add controlled variation to prevent identical values
    np.random.seed(42)
    df_enhanced['variation_factor'] = np.random.normal(0, 0.1, len(df_enhanced))

    # Apply variation to continuous features
    for col in ['anomaly_signal', 'public_access_score']:
        if col in df_enhanced.columns:
            df_enhanced[col] = df_enhanced[col] + df_enhanced['variation_factor'] * 0.5

    logger.info(f"Created strong discriminative features. Main discriminator distribution:")
    if len(df_enhanced) > 0:
        disc_counts = df_enhanced['main_discriminator'].value_counts()
        logger.info(f"  Private (0): {(df_enhanced['main_discriminator'] < 0.5).sum()}")
        logger.info(f"  Public (1): {(df_enhanced['main_discriminator'] >= 0.5).sum()}")

    return df_enhanced


def create_basic_discriminative_features(df):
    """
    Fallback: Create basic but effective discriminative features.
    """
    df_basic = df.copy()

    # Main discriminator based on ACL or public indicators
    if 'is_public_acl' in df.columns:
        df_basic['main_discriminator'] = df_basic['is_public_acl'].astype(float)
    elif 'acl' in df.columns:
        df_basic['main_discriminator'] = df_basic['acl'].apply(
            lambda x: 1.0 if str(x).lower() in ['public-read', 'public-read-write'] else 0.0
        )
    else:
        if 'source_file' in df.columns:
            df_basic['main_discriminator'] = df_basic['source_file'].apply(
                lambda x: 1.0 if 'misconfig' in str(x).lower() else 0.0
            )
        else:
            df_basic['main_discriminator'] = 0.0

    # Security level
    security_features = ['versioning_enabled', 'logging_enabled', 'encryption_enabled']
    available_security = [f for f in security_features if f in df.columns]

    if available_security:
        df_basic['security_level'] = df_basic[available_security].sum(axis=1).astype(float)
    else:
        df_basic['security_level'] = 0.0

    # Add variation
    np.random.seed(42)
    df_basic['variation'] = np.random.normal(0, 0.05, len(df_basic))
    df_basic['main_discriminator'] += df_basic['variation']
    df_basic['security_level'] += np.random.normal(0, 0.1, len(df_basic))

    return df_basic


def augment_dataset_improved(df, target_size=100):
    """
    Improved dataset augmentation with better strategies.
    """
    current_size = len(df)
    if current_size >= target_size:
        return df

    logger.info(f"Augmenting dataset from {current_size} to {target_size} samples")

    augmented_samples = []

    # Strategy 1: Create variations of existing samples
    n_variations = (target_size - current_size) // 2
    for i in range(n_variations):
        # Select a random sample
        idx = np.random.randint(0, len(df))
        sample = df.iloc[idx].copy()

        # Create variation
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['bucket_name', 'source_file'] and not col.endswith('_score'):
                # Add small perturbation
                if col in ['main_discriminator', 'is_public_acl', 'has_public_policy']:
                    # For critical binary features, occasionally flip
                    if np.random.random() < 0.1:  # 10% chance
                        sample[col] = 1 - sample[col]
                else:
                    # For other features, add noise
                    noise = np.random.normal(0, 0.1)
                    sample[col] = np.clip(sample[col] + noise, 0, 10)

        sample['bucket_name'] = f"{sample['bucket_name']}_var_{i}"
        sample['source_file'] = f"{sample['source_file']}_variation"
        augmented_samples.append(sample)

    # Strategy 2: Create interpolations between samples
    n_interpolations = target_size - current_size - n_variations
    for i in range(n_interpolations):
        # Select two random samples
        idx1, idx2 = np.random.choice(len(df), 2, replace=False)
        sample1 = df.iloc[idx1]
        sample2 = df.iloc[idx2]

        # Interpolate numeric features
        alpha = np.random.beta(2, 2)  # Beta distribution favors middle values
        new_sample = {}

        for col in df.columns:
            if col in ['bucket_name', 'source_file']:
                new_sample[col] = f"interpolated_{i}"
            elif col in ['acl']:
                # For categorical, choose one of the two
                new_sample[col] = sample1[col] if alpha < 0.5 else sample2[col]
            elif df[col].dtype in [np.float64, np.int64]:
                # Interpolate numeric features
                new_sample[col] = alpha * sample1[col] + (1 - alpha) * sample2[col]

                # For binary features, round to 0 or 1
                if col in ['is_public_acl', 'has_public_policy', 'versioning_enabled',
                           'logging_enabled', 'encryption_enabled']:
                    new_sample[col] = round(new_sample[col])
            else:
                new_sample[col] = sample1[col]

        augmented_samples.append(pd.Series(new_sample))

    # Combine original and augmented data
    augmented_df = pd.DataFrame(augmented_samples)
    combined_df = pd.concat([df, augmented_df], ignore_index=True)

    logger.info(f"Dataset augmented to {len(combined_df)} samples")
    return combined_df


def create_balanced_splits(df, test_size=0.3, val_size=0.2):
    """
    Create balanced train/test/val splits that preserve the distribution of anomalies.
    """
    # Check if we have labels for stratification
    if 'assumed_anomalous' in df.columns:
        y = df['assumed_anomalous'].values

        # Get feature columns (exclude metadata)
        feature_cols = [col for col in df.columns
                        if col not in ['bucket_name', 'source_file', 'assumed_anomalous', 'acl']]
        X = df[feature_cols].values

        # Ensure we have enough samples for stratification
        if len(np.unique(y)) > 1 and np.min(np.bincount(y)) >= 3:
            # Stratified split to maintain anomaly ratio
            X_train_val, X_test, y_train_val, y_test = train_test_split(
                X, y, test_size=test_size, stratify=y, random_state=42
            )

            if val_size > 0 and len(y_train_val) > 6:
                val_ratio = val_size / (1 - test_size)
                if np.min(np.bincount(y_train_val)) >= 2:
                    X_train, X_val, y_train, y_val = train_test_split(
                        X_train_val, y_train_val, test_size=val_ratio,
                        stratify=y_train_val, random_state=42
                    )
                else:
                    X_train, X_val, y_train, y_val = train_test_split(
                        X_train_val, y_train_val, test_size=val_ratio, random_state=42
                    )
            else:
                X_train, X_val = X_train_val, None
                y_train, y_val = y_train_val, None

            return (X_train, X_test, X_val), (y_train, y_test, y_val), feature_cols
        else:
            logger.warning("Cannot stratify split - insufficient samples per class")

    # Fallback to random split
    feature_cols = [col for col in df.columns
                    if col not in ['bucket_name', 'source_file', 'assumed_anomalous', 'acl']]
    X = df[feature_cols].values

    # Simple random split
    indices = np.arange(len(X))
    np.random.shuffle(indices)

    test_idx = int(len(X) * (1 - test_size))
    val_idx = int(test_idx * (1 - val_size))

    X_train = X[indices[:val_idx]]
    X_val = X[indices[val_idx:test_idx]] if val_size > 0 else None
    X_test = X[indices[test_idx:]]

    return (X_train, X_test, X_val), (None, None, None), feature_cols


def extract_features_main(terraform_dir, output_dir):
    """
    Main function for FIXED feature extraction pipeline.
    """
    # Create necessary directories
    os.makedirs(f"{output_dir}/features", exist_ok=True)

    # Extract and engineer features
    console.print("[cyan]Starting FIXED feature extraction...[/cyan]")
    features_df, selected_features, scaler = extract_features(terraform_dir)

    # Add soft labels based on source file path for evaluation
    console.print("[cyan]Adding evaluation labels...[/cyan]")
    features_df['assumed_anomalous'] = features_df['source_file'].apply(
        lambda x: 1 if 'misconfig' in str(x) else 0
    )

    # Log class distribution
    if 'assumed_anomalous' in features_df.columns:
        anomaly_count = features_df['assumed_anomalous'].sum()
        normal_count = len(features_df) - anomaly_count
        anomaly_ratio = anomaly_count / len(features_df) if len(features_df) > 0 else 0
        logger.info(
            f"Class distribution - Normal: {normal_count}, Anomalous: {anomaly_count}, Ratio: {anomaly_ratio:.3f}")

        # Verify we have separation in main features
        if 'main_discriminator' in features_df.columns:
            public_mean = features_df[features_df['assumed_anomalous'] == 1]['main_discriminator'].mean()
            private_mean = features_df[features_df['assumed_anomalous'] == 0]['main_discriminator'].mean()
            logger.info(f"Feature separation - Public mean: {public_mean:.3f}, Private mean: {private_mean:.3f}")

    # Save raw features with enhanced engineering
    features_path = f"{output_dir}/features/raw_features.csv"
    features_df.to_csv(features_path, index=False)
    logger.info(f"Saved engineered features to {features_path}")

    # Create balanced splits
    console.print("[cyan]Creating balanced data splits...[/cyan]")
    (X_train, X_test, X_val), (y_train, y_test, y_val), feature_names = create_balanced_splits(features_df)

    # Final feature scaling optimized for anomaly detection
    scaler = RobustScaler()  # RobustScaler is less sensitive to outliers
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_val_scaled = scaler.transform(X_val) if X_val is not None else None

    # Save processed datasets
    np.save(f"{output_dir}/features/X_train.npy", X_train_scaled)
    np.save(f"{output_dir}/features/X_test.npy", X_test_scaled)
    if X_val_scaled is not None:
        np.save(f"{output_dir}/features/X_val.npy", X_val_scaled)

    # Save labels if available
    if y_test is not None:
        np.save(f"{output_dir}/features/y_test.npy", y_test)
        if y_val is not None:
            np.save(f"{output_dir}/features/y_val.npy", y_val)

    # Save feature names and scaler
    pd.DataFrame({'feature_name': feature_names}).to_csv(
        f"{output_dir}/features/feature_names.csv", index=False
    )
    import pickle
    with open(f"{output_dir}/features/scaler.pkl", 'wb') as f:
        pickle.dump(scaler, f)

    console.print(f"[green]FIXED feature extraction completed.[/green]")
    console.print(f"[green]Processed {len(features_df)} configurations with {len(feature_names)} features.[/green]")

    # Print feature summary
    console.print("\n[bold]FIXED Feature Engineering Summary:[/bold]")
    console.print(f"  - Total configurations: {len(features_df)}")
    console.print(f"  - Selected features: {len(feature_names)}")
    console.print(f"  - Training samples: {len(X_train_scaled)}")
    console.print(f"  - Test samples: {len(X_test_scaled)}")
    if X_val_scaled is not None:
        console.print(f"  - Validation samples: {len(X_val_scaled)}")

    if y_test is not None:
        test_anomaly_ratio = np.mean(y_test)
        console.print(f"  - Test set anomaly ratio: {test_anomaly_ratio:.3f}")


if __name__ == "__main__":
    # If run directly, use default paths
    terraform_dir = "data/terraform"
    output_dir = "data/output"
    extract_features_main(terraform_dir, output_dir)