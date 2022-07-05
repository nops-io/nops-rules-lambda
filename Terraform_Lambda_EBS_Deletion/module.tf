data "archive_file" "main" {
  type        = "zip"
  source_file = "${path.module}/src/unused_ebs_lambda.py"
  output_path = "${path.module}/src/unused_ebs_lambda.zip"
}