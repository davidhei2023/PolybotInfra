variable "cluster_name" {
  description = "The name of your EKS cluster"
  type        = string
  default     = "davidhei-eks-cluster"
}

variable "aws_region" {
  description = "The AWS region to deploy in"
  type        = string
  default     = "us-east-2"
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
  default     = ["subnet-003d39a7e2f59f7ea", "subnet-04000561778b910f1", "subnet-0b1b3ede9f956fd5d"]
}

variable "desired_capacity" {
  description = "Desired number of nodes in the EKS node group"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of nodes in the EKS node group"
  type        = number
  default     = 5
}

variable "min_capacity" {
  description = "Minimum number of nodes in the EKS node group"
  type        = number
  default     = 1
}

variable "instance_type" {
  description = "The type of EC2 instance to use for worker nodes"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "The name of the key pair to use for SSH access to the EC2 instances"
  type        = string
  default     = "davidhei-ohio-key"
}

variable "control_plane_sg_ids" {
  description = "The IDs of the security groups to attach to the control-plane node"
  type        = list(string)
  default     = ["sg-0e25deee5189c83d9"]
}

variable "worker_node_sg_ids" {
  description = "The IDs of the security groups to attach to the worker nodes"
  type        = list(string)
  default     = ["sg-0e25deee5189c83d9"]
}

variable "ami_id" {
  description = "The AMI ID to use for the worker nodes"
  type        = string
  default     = "ami-0862be96e41dcbf74"  # Added the AMI ID from the merged config
}

variable "control_plane_iam_role" {
  description = "The IAM role to use for the EKS control plane"
  type        = string
  default     = "davidhei-k8s-control-plane-role"  # Added control plane IAM role
}

variable "worker_node_iam_role" {
  description = "The IAM role to use for the EKS worker nodes"
  type        = string
  default     = "davidhei-k8s-worker-node-role"  # Added worker node IAM role
}
