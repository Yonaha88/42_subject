/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checker_revrotate_bonus.c                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:10:51 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:26:43 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "checker_bonus.h"

static void	rev_rotate_op_checker(t_list **node_ptr)
{
	t_list	*first;
	t_list	*last;
	t_list	*tmp;

	if (*node_ptr == NULL || (*node_ptr)->next == NULL)
		return ;
	first = *node_ptr;
	last = *node_ptr;
	tmp = *node_ptr;
	while (last->next != NULL)
		last = last->next;
	while (tmp->next != last)
		tmp = tmp->next;
	tmp->next = NULL;
	last->next = first;
	*node_ptr = last;
}

void	rra_checker(t_list **a_lst)
{
	rev_rotate_op_checker(a_lst);
}

void	rrb_checker(t_list **b_lst)
{
	rev_rotate_op_checker(b_lst);
}

void	rrr_checker(t_list **a_lst, t_list **b_lst)
{
	rev_rotate_op_checker(a_lst);
	rev_rotate_op_checker(b_lst);
}
