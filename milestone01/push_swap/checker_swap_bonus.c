/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checker_swap_bonus.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:10:40 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:26:49 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "checker_bonus.h"

static void	swap_op_checker(t_list **node_ptr)
{
	t_list	*node;
	t_list	*next;

	node = *node_ptr;
	if (node != NULL && node->next != NULL)
	{
		next = node->next;
		node->next = next->next;
		next->next = node;
		*node_ptr = next;
	}
}

void	sa_checker(t_list **a_lst)
{
	swap_op_checker(a_lst);
}

void	sb_checker(t_list **b_lst)
{
	swap_op_checker(b_lst);
}

void	ss_checker(t_list **a_lst, t_list **b_lst)
{
	swap_op_checker(a_lst);
	swap_op_checker(b_lst);
}
