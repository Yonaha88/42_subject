/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checker_push_bonus.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:11:01 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:26:38 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "checker_bonus.h"

static void	push_op_checker(t_list **to, t_list **from)
{
	t_list	*from_node;

	from_node = *from;
	if (from_node != NULL)
	{
		*from = from_node->next;
		from_node->next = *to;
		*to = from_node;
	}
}

void	pa_checker(t_list **a_lst, t_list **b_lst)
{
	push_op_checker(a_lst, b_lst);
}

void	pb_checker(t_list **a_lst, t_list **b_lst)
{
	push_op_checker(b_lst, a_lst);
}
