/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   chunk_based_sort.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:10:34 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:27:01 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	root(int lst_count)
{
	int	r;

	r = 0;
	while ((long)(r * r) <= 2147483647)
	{
		if ((r * r > lst_count))
			break ;
		r++;
	}
	return (r);
}

static void	do_rotate_b(t_list **b_lst, int rotate_count, int b_size,
			t_data *bench_data)
{
	if (rotate_count <= b_size / 2)
	{
		while (rotate_count-- > 0)
			rb(b_lst, bench_data);
	}
	else
	{
		rotate_count = b_size - rotate_count;
		while (rotate_count-- > 0)
			rrb(b_lst, bench_data);
	}
}

static void	rotate_to_rank(t_list **b_lst, int count, t_data *bench_data)
{
	int		rotate_count;
	int		b_size;
	t_list	*lst;

	b_size = lst_count(*b_lst);
	rotate_count = 0;
	lst = *b_lst;
	while (lst != NULL)
	{
		if (count == lst->rank)
			break ;
		rotate_count++;
		lst = lst->next;
	}
	do_rotate_b(b_lst, rotate_count, b_size, bench_data);
}

static void	chunk_based_sort2(t_list **a_lst, t_list **b_lst, int count,
		t_data *bench_data)
{
	while (count >= 0)
	{
		rotate_to_rank(b_lst, count, bench_data);
		pa(a_lst, b_lst, bench_data);
		count--;
	}
}

void	chunk_based_sort(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	int	count;
	int	remaining;
	int	i;
	int	r;

	i = 0;
	count = lst_count(*a_lst);
	r = root(count);
	while (i <= r)
	{
		remaining = lst_count(*a_lst);
		while (remaining > 0)
		{
			if (i * r <= (*a_lst)->rank && (*a_lst)->rank < (i + 1) * r)
				pb(a_lst, b_lst, bench_data);
			else
				ra(a_lst, bench_data);
			remaining--;
		}
		i++;
	}
	chunk_based_sort2(a_lst, b_lst, count - 1, bench_data);
}
