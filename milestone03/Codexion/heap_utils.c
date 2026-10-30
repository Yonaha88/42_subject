/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   heap_utils.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:26 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:23:27 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	request_before(t_request *a, t_request *b)
{
	if (a->key != b->key)
		return (a->key < b->key);
	return (a->ticket < b->ticket);
}

static void	swap_requests(t_request *a, t_request *b)
{
	t_request	tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

void	sift_up(t_heap *h, int i)
{
	int	parent;

	while (i > 0)
	{
		parent = (i - 1) / 2;
		if (!request_before(&h->items[i], &h->items[parent]))
			return ;
		swap_requests(&h->items[i], &h->items[parent]);
		i = parent;
	}
}

void	sift_down(t_heap *h, int i)
{
	int	child;
	int	best;

	while (1)
	{
		best = i;
		child = 2 * i + 1;
		if (child < h->size
			&& request_before(&h->items[child], &h->items[best]))
			best = child;
		child++;
		if (child < h->size
			&& request_before(&h->items[child], &h->items[best]))
			best = child;
		if (best == i)
			return ;
		swap_requests(&h->items[i], &h->items[best]);
		i = best;
	}
}
