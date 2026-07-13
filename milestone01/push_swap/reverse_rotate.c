/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   reverse_rotate.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/14 13:43:06 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/19 18:24:33 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	reverse_rotate(t_list **node_ptr)
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

void	rra(t_list **a_lst, t_data *bench_data)
{
	reverse_rotate(a_lst);
	write(1, "rra\n", 4);
	bench_data->rra_cnt++;
	bench_data->total++;
}

void	rrb(t_list **b_lst, t_data *bench_data)
{
	reverse_rotate(b_lst);
	write(1, "rrb\n", 4);
	bench_data->rrb_cnt++;
	bench_data->total++;
}

void	rrr(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	reverse_rotate(a_lst);
	reverse_rotate(b_lst);
	write(1, "rrr\n", 4);
	bench_data->rrr_cnt++;
	bench_data->total++;
}
