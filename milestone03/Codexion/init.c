/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   init.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:17 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/27 15:08:49 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	init_base(t_table *t)
{
	if (pthread_mutex_init(&t->stop_mutex, NULL) != 0)
		return (0);
	t->ready_base++;
	if (pthread_mutex_init(&t->log_mutex, NULL) != 0)
		return (0);
	t->ready_base++;
	if (pthread_mutex_init(&t->arbiter, NULL) != 0)
		return (0);
	t->ready_base++;
	if (pthread_cond_init(&t->ready, NULL) != 0)
		return (0);
	t->ready_base++;
	return (1);
}

static int	init_dongles(t_table *t)
{
	while (t->ready_dongles < t->args.number_of_coders)
	{
		if (pthread_mutex_init(&t->dongles[t->ready_dongles].mutex, NULL) != 0)
			return (0);
		t->ready_dongles++;
	}
	return (1);
}

static void	link_coder(t_table *t, int i)
{
	t_coder	*c;

	c = &t->coders[i];
	c->id = i + 1;
	c->table = t;
	c->first = &t->dongles[i];
	c->second = &t->dongles[(i + 1) % t->args.number_of_coders];
}

static int	init_coders(t_table *t)
{
	t_coder	*c;

	while (t->ready_coders < t->args.number_of_coders)
	{
		c = &t->coders[t->ready_coders];
		link_coder(t, t->ready_coders);
		if (pthread_mutex_init(&c->state_mutex, NULL) != 0)
			return (0);
		if (pthread_cond_init(&c->wake, NULL) != 0)
		{
			pthread_mutex_destroy(&c->state_mutex);
			return (0);
		}
		t->ready_coders++;
	}
	return (1);
}

int	init_table(t_table *t)
{
	size_t	n;

	n = t->args.number_of_coders;
	t->dongles = malloc(sizeof(t_dongle) * n);
	t->coders = malloc(sizeof(t_coder) * n);
	if (!t->dongles || !t->coders)
	{
		fprintf(stderr, "Error: out of memory\n");
		return (0);
	}
	memset(t->dongles, 0, sizeof(t_dongle) * n);
	memset(t->coders, 0, sizeof(t_coder) * n);
	if (!init_base(t) || !init_dongles(t) || !init_coders(t))
	{
		fprintf(stderr, "Error: failed to initialize thread resources\n");
		return (0);
	}
	return (1);
}
