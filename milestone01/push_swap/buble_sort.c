/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   buble_sort.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/14 13:43:24 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:26:29 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	find_min_pos(t_list *lst)
{
	int		min_rank;
	int		min_pos;
	int		pos;
	t_list	*tmp;

	min_rank = lst->rank;
	min_pos = 0;
	pos = 0;
	tmp = lst->next;
	while (tmp != NULL)
	{
		pos++;
		if (tmp->rank < min_rank)
		{
			min_rank = tmp->rank;
			min_pos = pos;
		}
		tmp = tmp->next;
	}
	return (min_pos);
}

void	buble_sort(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	int	n;
	int	min_pos;

	n = lst_count(*a_lst);
	while (n > 1)
	{
		min_pos = find_min_pos(*a_lst);
		if (min_pos <= n / 2)
			while (min_pos-- > 0)
				ra(a_lst, bench_data);
		else
		{
			min_pos = n - min_pos;
			while (min_pos-- > 0)
				rra(a_lst, bench_data);
		}
		pb(a_lst, b_lst, bench_data);
		n--;
	}
	while (*b_lst != NULL)
		pa(a_lst, b_lst, bench_data);
}
