/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   small_sort.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: hkanamit <hkanamit@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/19 12:20:52 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/21 11:46:11 by hkanamit         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	small_sort(t_list **a_lst, t_data *bench_data)
{
	int	x;
	int	y;
	int	z;

	x = (*a_lst)->rank;
	y = (*a_lst)->next->rank;
	z = (*a_lst)->next->next->rank;
	if (x < y && y > z && x < z)
	{
		sa(a_lst, bench_data);
		ra(a_lst, bench_data);
	}
	else if (x > y && y < z && x < z)
		sa(a_lst, bench_data);
	else if (x < y && y > z && x > z)
		rra(a_lst, bench_data);
	else if (x > y && y < z && x > z)
		ra(a_lst, bench_data);
	else if (x > y && y > z && x > z)
	{
		ra(a_lst, bench_data);
		sa(a_lst, bench_data);
	}
}

void	small_sort3(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	int	i;

	i = 5;
	while (i-- > 0)
	{
		if ((*a_lst)->rank == 0 || (*a_lst)->rank == 1)
			pb(a_lst, b_lst, bench_data);
		else
			ra(a_lst, bench_data);
	}
	small_sort(a_lst, bench_data);
	if ((*b_lst)->rank < (*b_lst)->next->rank)
		sb(b_lst, bench_data);
	pa(a_lst, b_lst, bench_data);
	pa(a_lst, b_lst, bench_data);
}

void	small_sort2(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	int	i;

	i = 4;
	while (i-- > 0)
	{
		if ((*a_lst)->rank == 0)
		{
			pb(a_lst, b_lst, bench_data);
			break ;
		}
		ra(a_lst, bench_data);
	}
	small_sort(a_lst, bench_data);
	pa(a_lst, b_lst, bench_data);
}

void	base_sort2(t_list **a_lst, t_list **b_lst, t_data *bench_data)
{
	int	count;

	count = lst_count(*a_lst);
	if (count == 2)
	{
		if ((*a_lst)->rank > (*a_lst)->next->rank)
			sa(a_lst, bench_data);
	}
	else if (count == 3)
		small_sort(a_lst, bench_data);
	else if (count == 4)
		small_sort2(a_lst, b_lst, bench_data);
	else if (count == 5)
		small_sort3(a_lst, b_lst, bench_data);
}

int	base_sort(t_list *a_lst, t_data *bench_data, char *argv[], int argc)
{
	t_list	*b_lst;

	b_lst = NULL;
	if (error_handle(argc, argv) == 0)
		return (1);
	a_lst = make_a_lst(&a_lst, argc, argv);
	if (!a_lst)
		return (1);
	make_rank(&a_lst);
	bench_data->dis = disorder(&a_lst, bench_data);
	if (bench_data->dis != 0)
		base_sort2(&a_lst, &b_lst, bench_data);
	if (bench_data->flag == 1)
		bench_mark(*bench_data);
	ft_lstclear(&a_lst);
	ft_lstclear(&b_lst);
	return (0);
}
