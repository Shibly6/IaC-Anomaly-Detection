# Terraform Security Analysis Report

## Summary

- **Total Configurations Analyzed**: 27
- **Anomalies Detected**: 16
- **Anomaly Rate**: 59.3%
- **Average Ensemble Score**: 0.372
- **Models Used**: isolation_forest, one_class_svm, autoencoder, local_outlier_factor

## High-Risk Configurations

The following configurations have high anomaly scores (>0.7):

### everyone-can-upload-bucket

- **Source File**: `/home/shibly/PycharmProjects/iac-anomaly-detection_v.1/IaC/s3_public_acl_extra_new_4.tf`
- **Ensemble Score**: 0.750
- **Public ACL**: Yes
- **Public Policy**: No

### public-data-unrestricted-bucket

- **Source File**: `/home/shibly/PycharmProjects/iac-anomaly-detection_v.1/IaC/s3_public_acl_extra_new_1.tf`
- **Ensemble Score**: 0.750
- **Public ACL**: Yes
- **Public Policy**: No

### open-bucket-example-new

- **Source File**: `/home/shibly/PycharmProjects/iac-anomaly-detection_v.1/IaC/s3_public_acl_new_4.tf`
- **Ensemble Score**: 0.750
- **Public ACL**: Yes
- **Public Policy**: No

### unprotected-data-lake-bucket

- **Source File**: `/home/shibly/PycharmProjects/iac-anomaly-detection_v.1/IaC/s3_public_acl_extra_new_6.tf`
- **Ensemble Score**: 0.750
- **Public ACL**: Yes
- **Public Policy**: No

### public-read-write-bucket

- **Source File**: `/home/shibly/PycharmProjects/iac-anomaly-detection_v.1/IaC/s3_public_read_write.tf`
- **Ensemble Score**: 0.750
- **Public ACL**: Yes
- **Public Policy**: No

### world-readable-new-bucket

- **Source File**: `/home/shibly/PycharmProjects/iac-anomaly-detection_v.1/IaC/s3_public_acl_new_2.tf`
- **Ensemble Score**: 0.750
- **Public ACL**: Yes
- **Public Policy**: No

## Detailed Results

| Bucket Name | Source File | Ensemble Score | Status | Public ACL | Public Policy |
|-------------|-------------|----------------|--------|------------|---------------|
| public-bucket | `s3_public.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| public-via-policy-bucket | `s3_public_policy.tf` | 0.006 | ✓ Normal | No | No |
| everyone-can-upload-bucket | `s3_public_acl_extra_new_4.tf` | 0.750 | 🚨 ANOMALY | Yes | No |
| anonymous-read-access-bucket | `s3_public_acl_extra_new_2.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| anonymous-access-new-bucket | `s3_public_acl_new_3.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| world-accessible-files-bucket | `s3_public_acl_extra_new_3.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| public-data-unrestricted-bucket | `s3_public_acl_extra_new_1.tf` | 0.750 | 🚨 ANOMALY | Yes | No |
| private-acl-bucket-1-new | `s3_private_acl_new_1.tf` | 0.006 | ✓ Normal | No | No |
| open-bucket-example-new | `s3_public_acl_new_4.tf` | 0.750 | 🚨 ANOMALY | Yes | No |
| private-acl-auth-read-bucket-new | `s3_private_acl_new_2.tf` | 0.062 | ✓ Normal | No | No |
| public-encrypted-bucket | `s3_public_encrypted.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| private-bucket | `s3_private.tf` | 0.006 | ✓ Normal | No | No |
| public-read-bucket-explicit | `s3_public_read.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| unprotected-data-lake-bucket | `s3_public_acl_extra_new_6.tf` | 0.750 | 🚨 ANOMALY | Yes | No |
| logs-bucket | `s3_public_with_logging.tf` | 0.006 | ✓ Normal | No | No |
| public-bucket-with-logging | `s3_public_with_logging.tf` | 0.534 | 🚨 ANOMALY | Yes | No |
| public-read-write-bucket | `s3_public_read_write.tf` | 0.750 | 🚨 ANOMALY | Yes | No |
| public-website-content-bucket | `s3_public_acl_extra_new_7.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| private-bucket-explicit | `s3_private_explicit.tf` | 0.006 | ✓ Normal | No | No |
| private-bucket-default | `s3_private_default.tf` | 0.006 | ✓ Normal | No | No |
| public-data-new-bucket | `s3_public_acl_new_1.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| world-readable-new-bucket | `s3_public_acl_new_2.tf` | 0.750 | 🚨 ANOMALY | Yes | No |
| private-acl-private-bucket-3-new | `s3_private_acl_new_3.tf` | 0.006 | ✓ Normal | No | No |
| open-documents-share-bucket | `s3_public_acl_extra_new_5.tf` | 0.537 | 🚨 ANOMALY | Yes | No |
| private-bucket-with-policy | `s3_private_restrictive_policy.tf` | 0.006 | ✓ Normal | No | No |
| private-owner-control-bucket | `s3_private_owner_control.tf` | 0.006 | ✓ Normal | No | No |
| private-acl-auth-read-bucket-4-new | `s3_private_acl_new_4.tf` | 0.062 | ✓ Normal | No | No |
