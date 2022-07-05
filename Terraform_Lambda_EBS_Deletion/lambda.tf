resource "aws_lambda_function" "main" {
  filename         = data.archive_file.main.output_path
  role             = aws_iam_role.lambda.arn
  source_code_hash = data.archive_file.main.output_base64sha256

  runtime       = "python3.8"
  handler       = "lambda_function.lambda_handler"
  description   = "Lambda function that deletes the unused EBS volumes"
  function_name = "Delete_Unused_EBS"
  memory_size   = 128
  timeout       = 15

  reserved_concurrent_executions = 1


  tags = {
    Name = "Delete_Unused_EBS"
  }
}

resource "aws_lambda_permission" "main" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "ec2.amazonaws.com"
}
