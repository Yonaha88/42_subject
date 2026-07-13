/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checker_rotate_bonus.c                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:10:47 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:26:45 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "checker_bonus.h"

static void	rotate_op_checker(t_list **node_ptr)
{
	t_list	*first;
	t_list	*tmp;

	if (*node_ptr == NULL || (*node_ptr)->next == NULL)
		return ;
	tmp = *node_ptr;
	first = *node_ptr;
	while (tmp->next != NULL)
		tmp = tmp->next;
	tmp->next = first;
	*node_ptr = first->next;
	first->next = NULL;
}

void	ra_checker(t_list **a_lst)
{
	rotate_op_checker(a_lst);
}

void	rb_checker(t_list **b_lst)
{
	rotate_op_checker(b_lst);
}

void	rr_checker(t_list **a_lst, t_list **b_lst)
{
	rotate_op_checker(a_lst);
	rotate_op_checker(b_lst);
}
