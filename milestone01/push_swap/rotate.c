/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rotate.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/14 12:36:58 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/19 18:23:57 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	rotate(t_list **node_ptr)
{
	t_list	*first;
	t_list	*second;
	t_list	*tmp;

	if (*node_ptr == NULL || (*node_ptr)->next == NULL)
		return ;
	tmp = *node_ptr;
	first = *node_ptr;
	second = first->next;
	while (tmp->next != NULL)
		tmp = tmp->next;
	tmp->next = first;
	first->next = NULL;
	*node_ptr = second;
}

void	ra(t_list **a_lst, t_data *bench_data)
{
	rotate(a_lst);
	write(1, "ra\n", 3);
	bench_data->ra_cnt++;
	bench_data->total++;
}

void	rb(t_list **b_lst, t_data *bench_data)
{
	rotate(b_lst);
	write(1, "rb\n", 3);
	bench_data->rb_cnt++;
	bench_data->total++;
}

void	rr(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	rotate(a_lst);
	rotate(b_lst);
	write(1, "rr\n", 3);
	bench_data->rr_cnt++;
	bench_data->total++;
}
