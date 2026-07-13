/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/14 12:25:22 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/19 18:26:18 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	push(t_list **to, t_list **from)
{
	t_list	*to_node;
	t_list	*from_node;

	to_node = *to;
	from_node = *from;
	if (from_node != NULL)
	{
		*from = from_node->next;
		from_node->next = to_node;
		*to = from_node;
	}
}

void	pa(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	push(a_lst, b_lst);
	write(1, "pa\n", 3);
	bench_data->pa_cnt++;
	bench_data->total++;
}

void	pb(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	push(b_lst, a_lst);
	write(1, "pb\n", 3);
	bench_data->pb_cnt++;
	bench_data->total++;
}
