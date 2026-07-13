/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   disorder.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/15 11:10:55 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:27:04 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	disorder(t_list **a_lst, t_data *bench_data)
{
	size_t	mistakes;
	size_t	total_pairs;
	t_list	*i;
	t_list	*j;

	mistakes = 0;
	total_pairs = 0;
	i = *a_lst;
	while (i != NULL)
	{
		j = i->next;
		while (j != NULL)
		{
			total_pairs++;
			if (i->content > j->content)
				mistakes++;
			j = j->next;
		}
		i = i->next;
	}
	if (total_pairs == 0)
		return (0);
	bench_data->dis = (int)((mistakes * 10000) / total_pairs);
	return ((int)((mistakes * 10000) / total_pairs));
}
