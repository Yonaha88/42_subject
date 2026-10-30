/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   codexion.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:48 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/24 15:53:38 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	join_coders(t_table *t, int count)
{
	int	i;

	i = 0;
	while (i < count)
	{
		pthread_join(t->coders[i].thread, NULL);
		i++;
	}
}

static int	abort_start(t_table *t, int created)
{
	fprintf(stderr, "Error: failed to create a thread\n");
	stop_simulation(t);
	join_coders(t, created);
	return (0);
}

static void	start_clock(t_table *t)
{
	int	i;

	pthread_mutex_lock(&t->arbiter);
	while (t->arrived < t->args.number_of_coders)
		pthread_cond_wait(&t->ready, &t->arbiter);
	t->start = now_us();
	i = 0;
	while (i < t->args.number_of_coders)
		t->coders[i++].last_compile = t->start;
	t->started = 1;
	pthread_mutex_unlock(&t->arbiter);
	wake_all(t);
}

static int	run_simulation(t_table *t)
{
	int	i;

	i = 0;
	while (i < t->args.number_of_coders)
	{
		if (pthread_create(&t->coders[i].thread, NULL,
				coder_routine, &t->coders[i]) != 0)
			return (abort_start(t, i));
		i++;
	}
	if (t->args.number_of_compiles_required == 0)
		stop_simulation(t);
	start_clock(t);
	if (pthread_create(&t->monitor, NULL, monitor_routine, t) != 0)
		return (abort_start(t, i));
	pthread_join(t->monitor, NULL);
	join_coders(t, i);
	return (1);
}

int	main(int argc, char **argv)
{
	t_table	table;
	int		status;

	memset(&table, 0, sizeof(table));
	if (!parse_args(argc, argv, &table.args))
		return (1);
	status = 1;
	if (init_table(&table) && run_simulation(&table))
		status = 0;
	destroy_table(&table);
	return (status);
}
