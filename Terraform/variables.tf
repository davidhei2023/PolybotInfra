variable "cluster_name" {
  description = "The name of your EKS cluster"
  type        = string
}

variable "aws_region" {
  description = "The AWS region to deploy in"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
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
}

variable "control_plane_sg_ids" {
  description = "The IDs of the security groups to attach to the control-plane node"
  type        = list(string)
}

variable "worker_node_sg_ids" {
  description = "The IDs of the security groups to attach to the worker nodes"
  type        = list(string)
}
